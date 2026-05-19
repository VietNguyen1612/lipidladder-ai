"""ESC/EAS 2025 stepwise therapy engine.

Encodes Table 3 (risk categories), Table 4 / Figure 1 (LDL-C targets),
and the stepwise lipid-lowering ladder from §4.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RiskCategory = Literal["low", "moderate", "high", "very_high"]

THERAPY_STEPS: list[dict] = [
    {"id": "lifestyle",              "label": "Lifestyle only",                       "statin": "none",     "ezetimibe": False, "pcsk9": False, "bempedoic": False},
    {"id": "moderate_statin",        "label": "Moderate-intensity statin",            "statin": "moderate", "ezetimibe": False, "pcsk9": False, "bempedoic": False},
    {"id": "high_statin",            "label": "High-intensity statin",                "statin": "high",     "ezetimibe": False, "pcsk9": False, "bempedoic": False},
    {"id": "high_statin_eze",        "label": "High-intensity statin + ezetimibe",    "statin": "high",     "ezetimibe": True,  "pcsk9": False, "bempedoic": False},
    {"id": "high_statin_eze_bemp",   "label": "High-intensity statin + EZE + bempedoic acid", "statin": "high", "ezetimibe": True, "pcsk9": False, "bempedoic": True},
    {"id": "high_statin_eze_pcsk9",  "label": "High-intensity statin + EZE + PCSK9 inhibitor","statin": "high", "ezetimibe": True, "pcsk9": True,  "bempedoic": False},
    {"id": "max_combo",              "label": "High-intensity statin + EZE + PCSK9i + bempedoic acid","statin": "high", "ezetimibe": True, "pcsk9": True, "bempedoic": True},
]


@dataclass
class Patient:
    age: int
    sex: Literal["M", "F"]
    baseline_ldl: float   # mg/dL
    smoker: bool
    diabetes: bool
    ascvd: bool           # documented atherosclerotic CVD
    fh: bool              # familial hypercholesterolaemia
    ckd_egfr: float       # mL/min/1.73m^2
    sbp: int              # systolic BP
    total_chol: float     # mg/dL
    hdl: float            # mg/dL
    lp_a: float = 0.0     # nmol/L
    statin_intolerant: bool = False


def classify_risk(p: Patient) -> RiskCategory:
    """Simplified mapping of Table 3 (ESC/EAS 2025)."""
    if p.ascvd:
        return "very_high"
    if p.diabetes and (p.age > 40) and (p.smoker or p.sbp >= 140 or p.baseline_ldl >= 130):
        return "very_high"
    if p.ckd_egfr < 30:
        return "very_high"
    if p.fh and (p.ascvd or p.smoker or p.sbp >= 140):
        return "very_high"

    if p.baseline_ldl >= 190 or p.total_chol >= 310 or p.sbp >= 180:
        return "high"
    if p.fh:
        return "high"
    if 30 <= p.ckd_egfr < 60:
        return "high"

    # crude SCORE2-like surrogate
    score = 0
    score += (p.age - 40) * 0.15
    score += 2 if p.smoker else 0
    score += (p.sbp - 120) * 0.05
    score += (p.baseline_ldl - 100) * 0.02
    score += 3 if p.diabetes else 0
    score += 1.5 if p.sex == "M" else 0
    score += 1 if p.lp_a >= 105 else 0  # Lp(a) modifier per Box 1

    if score >= 10:
        return "high"
    if score >= 5:
        return "moderate"
    return "low"


def ldl_target(risk: RiskCategory) -> float:
    """Return LDL-C target in mg/dL per Figure 1."""
    if risk == "very_high":
        return 55.0
    if risk == "high":
        return 70.0
    if risk == "moderate":
        return 100.0
    return 116.0


def recommend_step(patient: Patient, predict_fn) -> dict:
    """Iterate through ladder, return minimum step achieving target.

    predict_fn(patient, step_dict) -> predicted post-treatment LDL (mg/dL)
    """
    risk = classify_risk(patient)
    target = ldl_target(risk)

    trajectory = []
    chosen = None
    for step in THERAPY_STEPS:
        pred = predict_fn(patient, step)
        # Patients who are statin-intolerant skip statin-only rungs
        viable = not (patient.statin_intolerant and step["statin"] != "none" and not step["ezetimibe"] and not step["pcsk9"])
        trajectory.append({"step": step, "predicted_ldl": pred, "viable": viable})
        if chosen is None and viable and pred <= target:
            chosen = step

    if chosen is None:
        chosen = THERAPY_STEPS[-1]

    return {
        "risk": risk,
        "target": target,
        "chosen_step": chosen,
        "trajectory": trajectory,
        "baseline_ldl": patient.baseline_ldl,
    }
