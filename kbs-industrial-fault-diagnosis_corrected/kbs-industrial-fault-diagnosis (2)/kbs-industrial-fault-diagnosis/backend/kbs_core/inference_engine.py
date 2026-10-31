"""
Inference Engine (forward chaining) for AI4I 2020 fault diagnosis.

How it works
------------
1. Working memory starts with the validated sensor readings (facts).
2. Derivation rules add new facts   : Temp_diff, Power, Strain.
3. Fault rules fire when all facts they need are available and their
   condition holds -> conclusions (fault + certainty factor).
4. The loop repeats until no rule can fire any more (forward chaining).
5. Conclusions are ranked by  priority = safety level x certainty.

All thresholds are read from knowledge_base.py (single source of truth).
Missing or physically impossible sensor values are NOT guessed: the rules
that need them are skipped and reported as "not evaluated".
"""
import math
import re

from backend.kbs_core.knowledge_base import KNOWLEDGE_BASE as KB

AIR, PROC = "Air temperature [K]", "Process temperature [K]"
RPM, TORQUE, WEAR = "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"

# Same plausible ranges used in the data-cleaning notebook.
VALID_RANGES = {AIR: (273, 350), PROC: (273, 350), RPM: (0, 4000),
                TORQUE: (0, 100), WEAR: (0, 300)}
EXCLUSIVE_LOWER = (RPM, TORQUE)

# ---------------------------------------------------------------- thresholds
def _trigger(code):
    return KB[code]["Technical_Details"]["Mathematical_Trigger"]

HDF_DELTA = KB["HDF"]["Variant_Profiles"]["L"]["Thermal_Delta_Threshold"]
HDF_RPM = int(re.search(r"<\s*(\d+)\s*RPM", _trigger("HDF")).group(1))
PWF_LOW, PWF_HIGH = [int(x) for x in re.findall(r"(\d+)\s*Watts", _trigger("PWF"))]
OSF_LIMITS = {t: p["Max_Strain_Product"] for t, p in KB["OSF"]["Variant_Profiles"].items()}
TWF_LOW = KB["TWF"]["Variant_Profiles"]["L"]["Risk_Window_Start"]
TWF_HIGH = KB["TWF"]["Variant_Profiles"]["L"]["Max_Wear_Limit"]

# Certainty factors. HDF/PWF/OSF rules reproduced the dataset labels 100 % in
# our check, so CF = 1.0. TWF: only ~5 % of rows inside the 200-240 min window
# were labelled TWF in the data (32 of 667), so it is a RISK, not a certainty.
TWF_CF = 0.05
RNF_CF = 0.5   # ASSUMED: a failure was observed but no rule explains it


def safety_level(code):
    m = re.search(r"LEVEL-(\d)", KB[code]["Constraints_Matrix"]["Safety_Criticality"])
    return int(m.group(1)) if m else 3


# ---------------------------------------------------------------- helpers
def _missing(v):
    return v is None or (isinstance(v, float) and math.isnan(v)) or v == ""


def validate_reading(reading):
    """Return (facts, missing, invalid). Impossible values are dropped."""
    facts, missing, invalid = {}, [], []
    for col, (lo, hi) in VALID_RANGES.items():
        v = reading.get(col)
        if _missing(v):
            missing.append(col)
            continue
        v = float(v)
        bad = (v <= lo or v > hi) if col in EXCLUSIVE_LOWER else (v < lo or v > hi)
        if bad:
            invalid.append((col, v))
        else:
            facts[col] = v
    # Product type: use 'Type', else first letter of 'Product ID'
    t = reading.get("Type")
    if t not in ("L", "M", "H"):
        pid = reading.get("Product ID")
        t = pid[0] if isinstance(pid, str) and pid[:1] in ("L", "M", "H") else None
    if t:
        facts["Type"] = t
    return facts, missing, invalid


# ---------------------------------------------------------------- rules
# Derivation rules: new fact = function(existing facts)
DERIVE_RULES = [
    ("D1", "Temp_diff", [PROC, AIR], lambda f: f[PROC] - f[AIR],
     "Temp_diff = Process temperature - Air temperature"),
    ("D2", "Power", [TORQUE, RPM], lambda f: f[TORQUE] * f[RPM] * 2 * math.pi / 60,
     "Power = Torque x RPM x 2*pi/60"),
    ("D3", "Strain", [WEAR, TORQUE], lambda f: f[WEAR] * f[TORQUE],
     "Strain = Tool wear x Torque"),
]


# Fault rules: each returns (fired, detail, certainty, notes)
def _hdf(f):
    td, rpm = f["Temp_diff"], f[RPM]
    ok = td < HDF_DELTA and rpm < HDF_RPM
    return ok, (f"Temp difference {td:.1f} K ({'<' if td < HDF_DELTA else '>='} {HDF_DELTA} K) "
                f"and speed {rpm:.0f} rpm ({'<' if rpm < HDF_RPM else '>='} {HDF_RPM} rpm)"), 1.0, []


def _pwf(f):
    p = f["Power"]
    ok = p < PWF_LOW or p > PWF_HIGH
    side = "below" if p < PWF_LOW else "above" if p > PWF_HIGH else "inside"
    return ok, f"Power {p:.0f} W is {side} the safe range {PWF_LOW}-{PWF_HIGH} W", 1.0, []


def _osf(f):
    t, notes, cf = f.get("Type"), [], 1.0
    if t not in OSF_LIMITS:
        t = "L"
        cf = 0.8
        notes.append("Product type unknown: the lowest limit (type L) was used.")
    s, limit = f["Strain"], OSF_LIMITS[t]
    ok = s > limit
    return ok, f"Tool wear x Torque = {s:.0f} ({'>' if ok else '<='} {limit} for type {t})", (cf if ok else 1.0), (notes if ok else [])


def _twf(f):
    w = f[WEAR]
    ok = TWF_LOW <= w <= TWF_HIGH
    return ok, f"Tool wear {w:.0f} min ({'inside' if ok else 'outside'} the {TWF_LOW}-{TWF_HIGH} min risk window)", TWF_CF, \
        ["Dataset assigns TWF randomly inside this window: this is a risk, not a confirmed failure."] if ok else []


FAULT_RULES = [
    ("R-HDF", "HDF", [PROC, AIR, RPM], ["Temp_diff", RPM], _hdf, "FAULT"),
    ("R-PWF", "PWF", [TORQUE, RPM], ["Power"], _pwf, "FAULT"),
    ("R-OSF", "OSF", [WEAR, TORQUE], ["Strain"], _osf, "FAULT"),
    ("R-TWF", "TWF", [WEAR], [WEAR], _twf, "RISK"),
]


# ---------------------------------------------------------------- engine
def diagnose(reading, observed_failure=None):
    """
    reading          : dict / pandas Series with the sensor columns (+Type/Product ID)
    observed_failure : True if a failure was actually observed (optional).
                       Used only to flag an unexplained (possibly random) failure.
    """
    facts, missing, invalid = validate_reading(reading)
    raw_facts = dict(facts)
    trace, fired, checked = [], [], []
    done = set()

    changed = True
    while changed:                                   # forward-chaining loop
        changed = False
        for rid, out, needs, fn, text in DERIVE_RULES:
            if rid not in done and all(n in facts for n in needs):
                facts[out] = fn(facts)
                done.add(rid)
                changed = True
                trace.append(f"{rid}: {text} = {facts[out]:.2f}")
        for rid, code, _, needs, fn, status in FAULT_RULES:
            if rid not in done and all(n in facts for n in needs):
                ok, detail, cf, notes = fn(facts)
                done.add(rid)
                changed = True
                checked.append(code)
                trace.append(f"{rid} ({KB[code]['Failure_Mode_Name']}): "
                             f"{'FIRED' if ok else 'not met'} - {detail}")
                if ok:
                    fired.append(dict(code=code, name=KB[code]["Failure_Mode_Name"],
                                      status=status, certainty=cf, detail=detail,
                                      rule=KB[code]["Technical_Details"]["Mathematical_Trigger"],
                                      notes=notes))

    # Rules that could not run because data was missing/invalid
    not_evaluated = []
    for rid, code, raw_needs, _, _, _ in FAULT_RULES:
        if rid not in done:
            lacking = [n for n in raw_needs if n not in raw_facts]
            not_evaluated.append(dict(code=code, name=KB[code]["Failure_Mode_Name"],
                                      lacking=lacking))

    # RNF cannot be inferred from sensors; only flagged if a failure was seen
    # and no deterministic fault rule explains it.
    if observed_failure and not any(x["status"] == "FAULT" for x in fired):
        fired.append(dict(code="RNF", name=KB["RNF"]["Failure_Mode_Name"],
                          status="UNEXPLAINED", certainty=RNF_CF,
                          detail="A failure was observed but no fault rule explains it.",
                          rule=KB["RNF"]["Technical_Details"]["Mathematical_Trigger"],
                          notes=["RNF has no sensor rule; certainty is an assumed value."]))

    for x in fired:
        x["safety_level"] = safety_level(x["code"])
        x["priority"] = round(x["safety_level"] * x["certainty"], 3)
    fired.sort(key=lambda x: x["priority"], reverse=True)

    if any(x["status"] == "FAULT" for x in fired):
        overall = "FAULT DETECTED"
    elif fired:
        overall = "RISK / UNEXPLAINED"
    elif not checked:
        overall = "INSUFFICIENT DATA"
    elif not_evaluated:
        overall = "NORMAL (PARTIAL DATA)"
    else:
        overall = "NORMAL"

    return dict(overall=overall, conclusions=fired, facts=facts, missing=missing,
                invalid=invalid, not_evaluated=not_evaluated, trace=trace)


# ---------------------------------------------------------------- evaluation
def evaluate(df):
    """Compare rule conclusions with the dataset labels (for the report)."""
    import pandas as pd
    flags = {c: [] for c in ("TWF", "HDF", "PWF", "OSF")}
    any_fault = []
    for _, row in df.iterrows():
        d = diagnose(row)
        got = {x["code"] for x in d["conclusions"]}
        for c in flags:
            flags[c].append(c in got)
        any_fault.append(d["overall"] == "FAULT DETECTED")
    out = []
    for c, pred in flags.items():
        pred = pd.Series(pred, index=df.index)
        y = df[c] == 1
        tp = int((pred & y).sum())
        out.append(dict(Fault=c, Labelled=int(y.sum()), RuleFired=int(pred.sum()),
                        Correct=tp, Precision=round(tp / max(pred.sum(), 1), 3),
                        Recall=round(tp / max(y.sum(), 1), 3)))
    return pd.DataFrame(out)
