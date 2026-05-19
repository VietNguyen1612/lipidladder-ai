"""Train a GradientBoosting regressor to predict post-treatment LDL-C.

Inputs : patient features + therapy assignment.
Output : predicted LDL-C (mg/dL).
"""
from __future__ import annotations

import argparse
import os
from typing import TYPE_CHECKING

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

if TYPE_CHECKING:
    from engine.ladder import Patient

FEATURES = [
    "age", "sex_M", "baseline_ldl", "smoker", "diabetes", "ascvd", "fh",
    "ckd_egfr", "sbp", "total_chol", "hdl", "lp_a",
    "statin_moderate", "statin_high", "ezetimibe", "pcsk9", "bempedoic",
]


def _encode(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out["age"] = df["age"]
    out["sex_M"] = (df["sex"] == "M").astype(int)
    for col in ["baseline_ldl", "ckd_egfr", "sbp", "total_chol", "hdl", "lp_a"]:
        out[col] = df[col]
    for col in ["smoker", "diabetes", "ascvd", "fh", "ezetimibe", "pcsk9", "bempedoic"]:
        out[col] = df[col].astype(int)
    out["statin_moderate"] = (df["statin"] == "moderate").astype(int)
    out["statin_high"] = (df["statin"] == "high").astype(int)
    return out[FEATURES]


def train(cohort_path: str = "data/cohort.csv", model_path: str = "model/ldl_model.joblib") -> dict:
    df = pd.read_csv(cohort_path)
    X = _encode(df)
    y = df["post_ldl"].to_numpy()

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(
        n_estimators=300, max_depth=4, learning_rate=0.05, random_state=42
    )
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    metrics = {
        "mae": float(mean_absolute_error(y_te, pred)),
        "r2": float(r2_score(y_te, pred)),
        "n_train": int(len(X_tr)),
        "n_test": int(len(X_te)),
    }

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "metrics": metrics}, model_path)
    print(f"Saved model to {model_path}")
    print(f"MAE = {metrics['mae']:.2f} mg/dL | R^2 = {metrics['r2']:.3f}")
    return metrics


def load(model_path: str = "model/ldl_model.joblib"):
    return joblib.load(model_path)


def predict_for_patient(bundle: dict, patient: "Patient", step: dict) -> float:
    raw = pd.DataFrame([{
        "age": patient.age, "sex": patient.sex, "baseline_ldl": patient.baseline_ldl,
        "smoker": patient.smoker, "diabetes": patient.diabetes,
        "ascvd": patient.ascvd, "fh": patient.fh,
        "ckd_egfr": patient.ckd_egfr, "sbp": patient.sbp,
        "total_chol": patient.total_chol, "hdl": patient.hdl, "lp_a": patient.lp_a,
        "statin": step["statin"], "ezetimibe": step["ezetimibe"],
        "pcsk9": step["pcsk9"], "bempedoic": step["bempedoic"],
    }])
    X = _encode(raw)[bundle["features"]]
    return float(bundle["model"].predict(X)[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", default="data/cohort.csv")
    parser.add_argument("--out", default="model/ldl_model.joblib")
    args = parser.parse_args()
    train(args.cohort, args.out)
