"""LipidLadder AI — Streamlit demo for ESC/EAS 2025 statin + ezetimibe topic.

Run:
  streamlit run app.py
"""
from __future__ import annotations

import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from engine.ladder import Patient, recommend_step, classify_risk, ldl_target, THERAPY_STEPS
from model import ldl_predictor

MODEL_PATH = "model/ldl_model.joblib"
COHORT_PATH = "data/cohort.csv"
CASES_PATH = "case_studies.json"


# ---------- bootstrap data + model on first run ----------
@st.cache_resource
def get_model_bundle():
    if not os.path.exists(MODEL_PATH):
        if not os.path.exists(COHORT_PATH):
            from data.synthetic_cohort import generate
            generate(2000, COHORT_PATH)
        ldl_predictor.train(COHORT_PATH, MODEL_PATH)
    return ldl_predictor.load(MODEL_PATH)


@st.cache_data
def load_cases():
    with open(CASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- UI ----------
st.set_page_config(page_title="LipidLadder AI", layout="wide", page_icon="💊")
st.title("💊 LipidLadder AI")
st.caption("ESC/EAS 2025 stepwise lipid-lowering recommender — statin + ezetimibe demo")

bundle = get_model_bundle()
cases = load_cases()

with st.sidebar:
    st.header("Patient input")

    case_names = ["(blank)"] + [c["name"] for c in cases]
    chosen_case = st.selectbox("Pre-loaded case", case_names, index=1)
    if chosen_case != "(blank)":
        case = next(c for c in cases if c["name"] == chosen_case)
        st.info(case["summary"])
        defaults = case["patient"]
    else:
        defaults = {
            "age": 55, "sex": "M", "baseline_ldl": 150,
            "smoker": False, "diabetes": False, "ascvd": False, "fh": False,
            "ckd_egfr": 90, "sbp": 130, "total_chol": 220, "hdl": 50,
            "lp_a": 20, "statin_intolerant": False,
        }

    age = st.slider("Age", 30, 90, defaults["age"])
    sex = st.radio("Sex", ["M", "F"], index=0 if defaults["sex"] == "M" else 1, horizontal=True)
    baseline_ldl = st.number_input("Untreated LDL-C (mg/dL)", 50.0, 350.0, float(defaults["baseline_ldl"]))
    total_chol = st.number_input("Total cholesterol (mg/dL)", 100.0, 450.0, float(defaults["total_chol"]))
    hdl = st.number_input("HDL-C (mg/dL)", 20.0, 110.0, float(defaults["hdl"]))
    sbp = st.slider("Systolic BP", 90, 220, int(defaults["sbp"]))
    ckd_egfr = st.slider("eGFR (mL/min/1.73m²)", 10.0, 130.0, float(defaults["ckd_egfr"]))

    col1, col2 = st.columns(2)
    smoker   = col1.checkbox("Smoker",   value=defaults["smoker"])
    diabetes = col2.checkbox("Diabetes", value=defaults["diabetes"])
    ascvd    = col1.checkbox("ASCVD",    value=defaults["ascvd"])
    fh       = col2.checkbox("FH",       value=defaults["fh"])
    intolerant = st.checkbox("Statin intolerant", value=defaults["statin_intolerant"])

    lp_a = st.number_input("Lp(a) (nmol/L)", 0.0, 400.0, float(defaults["lp_a"]))

# ---------- build patient + run recommendation ----------
patient = Patient(
    age=age, sex=sex, baseline_ldl=baseline_ldl, smoker=smoker, diabetes=diabetes,
    ascvd=ascvd, fh=fh, ckd_egfr=ckd_egfr, sbp=sbp, total_chol=total_chol, hdl=hdl,
    lp_a=lp_a, statin_intolerant=intolerant,
)

predict = lambda p, step: ldl_predictor.predict_for_patient(bundle, p, step)
result = recommend_step(patient, predict)

# ---------- output ----------
top = st.columns(3)
top[0].metric("Risk category", result["risk"].replace("_", " ").upper())
top[1].metric("LDL-C target", f"< {result['target']:.0f} mg/dL")
top[2].metric("Untreated LDL", f"{patient.baseline_ldl:.0f} mg/dL")

st.subheader("Recommended therapy step")
st.success(f"➡️  **{result['chosen_step']['label']}**")

st.subheader("Stepwise ladder — predicted LDL-C at each rung")
traj = result["trajectory"]
df = pd.DataFrame([
    {"Step": t["step"]["label"], "Predicted LDL": t["predicted_ldl"], "Viable": t["viable"]}
    for t in traj
])

fig, ax = plt.subplots(figsize=(9, 4.5))
colors = []
for t in traj:
    if not t["viable"]:
        colors.append("#aaaaaa")
    elif t["step"]["id"] == result["chosen_step"]["id"]:
        colors.append("#2e7d32")
    elif t["predicted_ldl"] <= result["target"]:
        colors.append("#a5d6a7")
    else:
        colors.append("#ef5350")
ax.barh(df["Step"], df["Predicted LDL"], color=colors)
ax.axvline(result["target"], linestyle="--", color="black", label=f"Target < {result['target']:.0f}")
ax.invert_yaxis()
ax.set_xlabel("Predicted post-treatment LDL-C (mg/dL)")
ax.legend(loc="lower right")
st.pyplot(fig)

with st.expander("Show numeric table"):
    st.dataframe(df.style.format({"Predicted LDL": "{:.1f}"}), width="stretch")

st.divider()
st.caption(
    f"Model: GradientBoostingRegressor | MAE = {bundle['metrics']['mae']:.2f} mg/dL · "
    f"R² = {bundle['metrics']['r2']:.3f} (n_test = {bundle['metrics']['n_test']})"
)
st.caption("Educational demo for the ESC/EAS 2025 Focused Update — not for clinical use.")
