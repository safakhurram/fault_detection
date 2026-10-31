"""
Explanation Generator: turns an inference-engine result into plain text that
tells the user WHAT was found, WHY (which rule and which values), HOW SURE the
system is, what the impact is and what to do.
"""
from backend.kbs_core.knowledge_base import KNOWLEDGE_BASE as KB


def explain(d, show_trace=True):
    L = []
    L.append(f"DIAGNOSIS: {d['overall']}")
    L.append("=" * 60)

    if not d["conclusions"]:
        if d["overall"].startswith("NORMAL"):
            L.append("All evaluated fault rules were checked and none fired.")
        elif d["overall"] == "INSUFFICIENT DATA":
            L.append("No fault rule could be evaluated because sensor data is missing or invalid.")

    for i, c in enumerate(d["conclusions"], 1):
        kb = KB[c["code"]]
        cm = kb["Constraints_Matrix"]
        L.append(f"\n[{i}] {c['name']} ({c['code']}) - {c['status']}, certainty {c['certainty']:.0%}")
        L.append(f"  Why      : {c['detail']}")
        L.append(f"  Rule     : {c['rule']}")
        for n in c["notes"]:
            L.append(f"  Note     : {n}")
        L.append(f"  Component: {kb['Target_Component']}")
        L.append(f"  Priority : {c['priority']} (safety level {c['safety_level']} x certainty {c['certainty']})")
        L.append(f"  Impact   : {cm['Safety_Criticality']}")
        L.append(f"             Downtime: {cm['Downtime_Impact']}")
        L.append(f"             Cost: {cm['Financial_Cost_Index']}")
        L.append("  Actions  :")
        for role, text in kb["Action_Protocols"].items():
            L.append(f"    - {role.replace('_Action', '').replace('_', ' ')}: {text}")

    if len(d["conclusions"]) > 1:
        L.append(f"\nMultiple faults found. Handle first: {d['conclusions'][0]['name']} "
                 "(highest safety level x certainty).")

    if d["missing"] or d["invalid"] or d["not_evaluated"]:
        L.append("\nDATA QUALITY")
        if d["missing"]:
            L.append(f"  Missing values : {', '.join(d['missing'])}")
        for col, v in d["invalid"]:
            L.append(f"  Impossible value ignored: {col} = {v}")
        for n in d["not_evaluated"]:
            L.append(f"  Not evaluated  : {n['name']} (lacking {', '.join(n['lacking'])})")

    if show_trace:
        L.append("\nREASONING TRACE (forward chaining)")
        for step in d["trace"]:
            L.append(f"  {step}")
    return "\n".join(L)


if __name__ == "__main__":
    from backend.kbs_core.inference_engine import diagnose
    case = {"Type": "L", "Air temperature [K]": 300.0, "Process temperature [K]": 308.5,
            "Rotational speed [rpm]": 1300, "Torque [Nm]": 65.0, "Tool wear [min]": 210}
    print(explain(diagnose(case)))
