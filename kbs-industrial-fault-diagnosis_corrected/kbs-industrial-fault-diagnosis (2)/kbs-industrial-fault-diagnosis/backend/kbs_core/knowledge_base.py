# =====================================================================
# AI4I 2020 PREDICTIVE MAINTENANCE: INDUSTRIAL KNOWLEDGE BASE (KB)
# Aligned with Dataset Specifications & Multi-Stakeholder Rubrics
# =====================================================================
# NOTE: "Mathematical_Trigger" thresholds come from the UCI AI4I 2020 dataset
# documentation. Safety levels, downtime, cost, machine-grade descriptions,
# risk labels and maintenance actions are ASSUMED engineering guidance
# (decision support only, not manufacturer procedures).
# =====================================================================

KNOWLEDGE_BASE = {
    "TWF": {
       "Failure_ID": "ERR-CNC-TWF-01",
       "Failure_Mode_Name": "Tool Wear Failure",
       "Target_Component": "CNC Spindle Axis & Carbide Cutting Tool Head",
       "ISO_Standard_Ref": "ISO 15641: Milling Cutters Safety Requirements",
    
        # Technical Engineering Core
        "Technical_Details": {
            "Definition": "The tool wear index gradually increments through abrasive friction during cutting operations until geometric cutting tolerances are lost.",
            "Observed_Symptom": "High surface roughness on workpiece, severe chattering/vibrations, and cutting friction noise.",
            "Mathematical_Trigger": "Tool wear [min] is within 200-240 min (risk window; the dataset assigns TWF randomly inside it for all types)."
        },
    
        # Dataset-Specific Constraints (L, M, H Variant Profiles)
        "Variant_Profiles": {
            "L": {"Machine_Grade": "Lite Quality", "Risk_Window_Start": 200, "Max_Wear_Limit": 240, "Failure_Risk_Multiplier": "High"},
            "M": {"Machine_Grade": "Medium Quality", "Risk_Window_Start": 200, "Max_Wear_Limit": 240, "Failure_Risk_Multiplier": "Medium"},
            "H": {"Machine_Grade": "High Quality", "Risk_Window_Start": 200, "Max_Wear_Limit": 240, "Failure_Risk_Multiplier": "Low"}
        },
    
        # Multi-Stakeholder Action Matrix (CLO 2 Requirement) - Updated safety protocol
        "Action_Protocols": {
            "Floor_Operator_Action": "Press Emergency Feed Hold (E-STOP). Do not attempt manual clearance.",
            "Maintenance_Technician_Action": "Isolate the spindle power drive. Unlock the tool changer chuck. Replace the worn cutting bit insert. Reset the tool length calibration sensor values.",
            "Plant_Manager_Action": "Log a 30-minute unscheduled maintenance stop. Route the current workpiece to the scrap/rework bin for inspection."
        },
        
        # System Constraints Impact (Judging Criteria Metrics)
        "Constraints_Matrix": {
            "Safety_Criticality": "LEVEL-2 (Low risk to human operator; high danger of tool breakage causing internal enclosure damage).",
            "Downtime_Impact": "Short-Term Asset Stop (25 to 35 Minutes replacement window).",
            "Financial_Cost_Index": "Low (Standard consumable cutting insert replacement expense).",
            "Production_Continuity": "Local asset halt; does not disrupt the main assembly line if inventory buffers exist."
        }
    },

    "HDF": {
       "Failure_ID": "ERR-COOL-HDF-02",
        "Failure_Mode_Name": "Heat Dissipation Failure",
        "Target_Component": "Liquid Coolant Loop Assembly & Thermal Radiator Fan",
        "ISO_Standard_Ref": "ISO 13374: Machine Condition Monitoring and Diagnostics",
        
        "Technical_Details": {
            "Definition": "Convective heat transfer capacity degrades due to fluid loss or blockage, causing thermal saturation.",
            "Observed_Symptom": "Rapid structural temperature spikes and reservoir warning indicators.",
            "Mathematical_Trigger": "Temperature difference (Process Temp - Air Temp) < 8.6 K AND Rotational speed < 1380 RPM."
        },
        
        "Variant_Profiles": {
            "L": {"Machine_Grade": "Lite Quality (Standard Radiator)", "Thermal_Delta_Threshold": 8.6, "Thermal_Sensitivity": "Critical"},
            "M": {"Machine_Grade": "Medium Quality (Enhanced Cooling)", "Thermal_Delta_Threshold": 8.6, "Thermal_Sensitivity": "High"},
            "H": {"Machine_Grade": "High Quality (Heavy Duty Dual Cooling)", "Thermal_Delta_Threshold": 8.6, "Thermal_Sensitivity": "Medium"}
        },
        
        "Action_Protocols": {
            "Floor_Operator_Action": "Safely park the CNC axis to home location. Shut off spindle rotational power to stop structural friction heat.",
            "Maintenance_Technician_Action": "Check the external coolant fluid volume. Verify pump drive contactor status. Clean radiator convective fins of metal dust blockages.",
            "Plant_Manager_Action": "Issue high-priority maintenance ticket. Keep machine powered down until the thermal block reaches room temperature equilibrium."
        },
        
        "Constraints_Matrix": {
            "Safety_Criticality": "LEVEL-4 (High Risk of fluid boiling, pressurized hose ruptures, or structural spindle block seizure).",
            "Downtime_Impact": "Long-Term Thermal Cool-Down Cycle (90 to 120 Minutes mandatory window).",
            "Financial_Cost_Index": "Medium (Potential coolant system overhaul and fluid recharge cost).",
            "Production_Continuity": "Critical Halt. Prolonged execution in this state will permanently warp the machine casting geometry."
        }
    },

    "PWF": {
        "Failure_ID": "ERR-ELEC-PWF-03",
        "Failure_Mode_Name": "Power Failure",
        "Target_Component": "Electrical Drive Inverter & Main Brushless DC Motor Windings",
        "ISO_Standard_Ref": "IEC 60204-1: Safety of Machinery - Electrical Equipment",
        
        "Technical_Details": {
            "Definition": "The electrical torque power delivered to the spindle drive is out of standard physical bounds, causing current overloads or torque stalls.",
            "Observed_Symptom": "Sudden rotational speed drops, breaker trips in the substation panel, humming noise from the motor.",
            "Mathematical_Trigger": "Power = Torque [Nm] * RPM * (2*pi/60) drops below 3500 Watts OR exceeds 9000 Watts."
        },
        
        "Variant_Profiles": {
            "L": {"Machine_Grade": "Lite Quality", "Safe_Power_Range": "3500W - 9000W", "Overcurrent_Risk": "Very High"},
            "M": {"Machine_Grade": "Medium Quality", "Safe_Power_Range": "3500W - 9000W", "Overcurrent_Risk": "Medium"},
            "H": {"Machine_Grade": "High Quality", "Safe_Power_Range": "3500W - 9000W", "Overcurrent_Risk": "Low"}
        },
        
        "Action_Protocols": {
            "Floor_Operator_Action": "Do not touch the physical chassis. Press E-STOP and follow the site electrical emergency procedure; only authorised personnel may isolate power.",
            "Maintenance_Technician_Action": "Qualified electrician only, after lockout/tagout: open the electrical enclosure cabinet. Use a multimeter to measure phases for voltage drops. Check the inverter fault history codes. Test motor winding insulation resistance.",
            "Plant_Manager_Action": "Call the authorized high-voltage industrial electrical team. Halt the downstream assembly track due to absolute line stoppage."
        },
        
        "Constraints_Matrix": {
            "Safety_Criticality": "LEVEL-5 (Extreme Danger of arc flash, severe electrocution hazard, or internal electrical fire).",
            "Downtime_Impact": "Indeterminate Technical Delay (Typically 2 to 4 hours depending on electrical component availability).",
            "Financial_Cost_Index": "High (Inverter drives or motor rewinding are expensive asset investments).",
            "Production_Continuity": "Total Department Halt. Affects power grid stability if the breaker fails to trip."
        }
    },

    "OSF": {
        "Failure_ID": "ERR-MECH-OSF-04",
        "Failure_Mode_Name": "Overstrain Failure",
        "Target_Component": "Linear Axis Guide Rails, Ball Screws & Heavy Duty Bearings",
        "ISO_Standard_Ref": "ISO 3408: Ball Screws - Technical Specifications & Tolerances",
        
        "Technical_Details": {
            "Definition": "The combination of severe mechanical feed load (torque) and degraded tool surface geometry causes physical structural stress beyond the framework limit.",
            "Observed_Symptom": "Extreme structural feedback vibrations, axis binding, frame cracking sounds.",
            "Mathematical_Trigger": "The product of Tool wear [min] and Torque [Nm] exceeds 11000 (L), 12000 (M), or 13000 (H)."
        },
        
        "Variant_Profiles": {
            "L": {"Machine_Grade": "Lite Quality", "Max_Strain_Product": 11000, "Structural_Yield": "Low"},
            "M": {"Machine_Grade": "Medium Quality", "Max_Strain_Product": 12000, "Structural_Yield": "Medium"},
            "H": {"Machine_Grade": "High Quality", "Max_Strain_Product": 13000, "Structural_Yield": "High"}
        },
        
        "Action_Protocols": {
            "Floor_Operator_Action": "Trigger emergency stop. Clear all workspace obstructions. Do not force manual axis jog movements.",
            "Maintenance_Technician_Action": "Inspect guide rails for scoring or structural distortion. Check ball screw backlash clearance. Verify the automatic oil lubrication lines are not blocked.",
            "Plant_Manager_Action": "Schedule an immediate axis geometric alignment cycle. Reduce standard machining feed rate parameters by 20% in the CNC program."
        },
        
        "Constraints_Matrix": {
            "Safety_Criticality": "LEVEL-3 (Medium Risk of component mechanical shearing or flying structural debris).",
            "Downtime_Impact": "Medium-Term Structural Maintenance (60 to 90 Minutes calibration window).",
            "Financial_Cost_Index": "Medium (Requires precision calibration equipment and rail greasing lubricants).",
            "Production_Continuity": "Localized machine stoppage; requires recalibration before processing the next production block."
        }
    },
    "RNF": {
        "Failure_ID": "ERR-GEN-RNF-05",
        "Failure_Mode_Name": "Random Failure",
        "Target_Component": "General Machine Assembly & Control Logic Subsystem",
        "ISO_Standard_Ref": "ISO 12100: Safety of Machinery - General Principles for Design",
        
        # Technical Engineering Core
        "Technical_Details": {
            "Definition": "Stochastic and unpredicted component breakdown occurring due to rare operational anomalies or latent material defects without deterministic sensor triggers.",
            "Observed_Symptom": "Sudden unexpected machine shutdown, unexplained controller error flags, or erratic actuator response.",
            "Mathematical_Trigger": "None (Occurs stochastically based on a baseline probability of ~0.1% independent of physical feature thresholds)."
        },
        
        # Dataset-Specific Constraints (L, M, H Variant Profiles)
        "Variant_Profiles": {
            "L": {"Machine_Grade": "Lite Quality", "Probability": "Stochastic (~0.1%)", "Risk_Level": "Unpredictable"},
            "M": {"Machine_Grade": "Medium Quality", "Probability": "Stochastic (~0.1%)", "Risk_Level": "Unpredictable"},
            "H": {"Machine_Grade": "High Quality", "Probability": "Stochastic (~0.1%)", "Risk_Level": "Unpredictable"}
        },
        
        # Multi-Stakeholder Action Matrix (CLO 2 Requirement)
        "Action_Protocols": {
            "Floor_Operator_Action": "Trigger Emergency Stop (E-STOP) immediately and notify the shift supervisor.",
            "Maintenance_Technician_Action": "Perform full diagnostic scan of PLC error logs, inspect wiring harnesses, and check general mechanical integrity.",
            "Plant_Manager_Action": "Log unpredicted asset downtime and review telemetry black-box logs for root-cause analysis."
        },
        
        # System Constraints Impact (Judging Criteria Metrics)
        "Constraints_Matrix": {
            "Safety_Criticality": "LEVEL-3 (Moderate Risk depending on the active operation during sudden stoppage).",
            "Downtime_Impact": "Variable Technical Delay (45 to 60 Minutes diagnostic window).",
            "Financial_Cost_Index": "Low to Medium (Depending on whether component replacement is required).",
            "Production_Continuity": "Unexpected local asset halt requiring manual inspection before resuming operations."
        }
    }
}
