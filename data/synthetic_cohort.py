"""Generate a synthetic patient cohort with post-treatment LDL-C labels.

Reductions are anchored to Figure 2 of the ESC/EAS 2025 Focused Update:
  moderate statin       ~30%
  high-intensity statin ~50%
  ezetimibe alone       ~20%
  bempedoic alone       ~23%
  EZE + bempedoic       ~38%
  high statin + EZE     ~60%
  high statin + bempedoic ~58%
  high statin + EZE + BA ~68%
  PCSK9 mAb             ~60%
  PCSK9 + statin        ~75%
  triple + PCSK9        ~80%
  quad therapy          ~86%
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

REDUCTION_PCT = {
    # (statin, ezetimibe, pcsk9, bempedoic) -> mean LDL reduction
    ("none",     False, False, False): 0.0,
    ("moderate", False, False, False): 0.30,
    ("high",     False, False, False): 0.50,
    ("none",     True,  False, False): 0.20,
    ("none",     False, False, True):  0.23,
    ("none",     True,  False, True):  0.38,
    ("moderate", True,  False, False): 0.45,
    ("high",     True,  False, False): 0.60,
    ("high",     False, False, True):  0.58,
    ("high",     True,  False, True):  0.68,
    ("none",     False, True,  False): 0.60,
    ("moderate", False, True,  False): 0.70,
    ("high",     False, True,  False): 0.75,
    ("high",     True,  True,  False): 0.80,
    ("high",     False, True,  True):  0.78,
    ("high",     True,  True,  True):  0.86,
}

THERAPY_COMBOS = list(REDUCTION_PCT.keys())


def _sample_patient(n: int) -> pd.DataFrame:
    age = RNG.integers(35, 85, n)
    sex = RNG.choice(["M", "F"], n, p=[0.55, 0.45])
    baseline_ldl = np.clip(RNG.normal(140, 35, n), 70, 280)
    smoker = RNG.random(n) < 0.25
    diabetes = RNG.random(n) < 0.20
    ascvd = RNG.random(n) < 0.22
    fh = RNG.random(n) < 0.05
    ckd_egfr = np.clip(RNG.normal(85, 20, n), 15, 130)
    sbp = np.clip(RNG.normal(135, 18, n), 95, 200).astype(int)
    total_chol = baseline_ldl + RNG.normal(70, 15, n)
    hdl = np.clip(RNG.normal(50, 12, n), 25, 95)
    lp_a = np.where(RNG.random(n) < 0.2, RNG.exponential(80, n), RNG.uniform(0, 30, n))

    return pd.DataFrame({
        "age": age, "sex": sex, "baseline_ldl": baseline_ldl,
        "smoker": smoker, "diabetes": diabetes, "ascvd": ascvd, "fh": fh,
        "ckd_egfr": ckd_egfr, "sbp": sbp, "total_chol": total_chol, "hdl": hdl,
        "lp_a": lp_a,
    })


def _apply_therapy(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, p in df.iterrows():
        # Each patient gets ~4 random therapy assignments to enrich training set
        combos = [THERAPY_COMBOS[i] for i in RNG.choice(len(THERAPY_COMBOS), size=4, replace=False)]
        for statin, eze, pcsk9, bemp in combos:
            base_reduction = REDUCTION_PCT[(statin, eze, pcsk9, bemp)]
            # Inter-individual variability (response heterogeneity)
            indiv_factor = RNG.normal(1.0, 0.12)
            # Slight effect modifiers
            if p["fh"] and statin != "none":
                indiv_factor *= 0.92  # FH less responsive to statin
            if p["age"] > 75 and statin == "high":
                indiv_factor *= 0.97
            reduction = np.clip(base_reduction * indiv_factor, 0, 0.92)
            post_ldl = p["baseline_ldl"] * (1 - reduction) + RNG.normal(0, 4)
            post_ldl = max(post_ldl, 15.0)
            row = p.to_dict()
            row.update({
                "statin": statin, "ezetimibe": eze,
                "pcsk9": pcsk9, "bempedoic": bemp,
                "post_ldl": post_ldl,
            })
            rows.append(row)
    return pd.DataFrame(rows)


def generate(n_patients: int = 2000, out_path: str = "data/cohort.csv") -> pd.DataFrame:
    base = _sample_patient(n_patients)
    cohort = _apply_therapy(base)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cohort.to_csv(out_path, index=False)
    print(f"Wrote {len(cohort)} rows to {out_path}")
    return cohort


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=2000)
    parser.add_argument("--out", type=str, default="data/cohort.csv")
    args = parser.parse_args()
    generate(args.n, args.out)
