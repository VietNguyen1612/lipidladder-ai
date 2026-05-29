"""LipidLadder AI — Streamlit demo for ESC/EAS 2025 statin + ezetimibe topic.

Run:
  streamlit run app.py
"""
from __future__ import annotations

import json
import os
from functools import partial

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from engine.ladder import Patient, recommend_step
from i18n import LANGUAGES, risk_label, step_label, t
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

# Language selector first so every label below can use it
lang_label = st.sidebar.selectbox(
    "🌐 " + " / ".join(LANGUAGES.keys()),
    list(LANGUAGES.keys()),
    index=1,
)
lang = LANGUAGES[lang_label]

st.title(t("app_title", lang))
st.caption(t("app_caption", lang))

bundle = get_model_bundle()
cases = load_cases()

with st.sidebar:
    st.header(t("patient_input", lang))

    case_names = [t("blank", lang)] + [c["name"] for c in cases]
    chosen_case = st.selectbox(t("preloaded_case", lang), case_names, index=1)
    case_explanation = None
    if chosen_case != t("blank", lang):
        case = next(c for c in cases if c["name"] == chosen_case)
        st.info(case["summary"])
        defaults = case["patient"]
        explanation = case.get("explanation")
        if explanation:
            case_explanation = explanation.get(lang) or explanation.get("en")
    else:
        defaults = {
            "age": 55, "sex": "M", "baseline_ldl": 150,
            "smoker": False, "diabetes": False, "ascvd": False, "fh": False,
            "ckd_egfr": 90, "sbp": 130, "total_chol": 220, "hdl": 50,
            "lp_a": 20, "statin_intolerant": False,
        }

    age = st.slider(t("age", lang), 30, 90, defaults["age"])
    sex_options = [t("sex_M", lang), t("sex_F", lang)]
    sex_choice = st.radio(
        t("sex", lang), sex_options,
        index=0 if defaults["sex"] == "M" else 1, horizontal=True,
    )
    sex = "M" if sex_choice == t("sex_M", lang) else "F"

    baseline_ldl = st.number_input(t("baseline_ldl", lang), 50.0, 350.0, float(defaults["baseline_ldl"]))
    total_chol = st.number_input(t("total_chol", lang), 100.0, 450.0, float(defaults["total_chol"]))
    hdl = st.number_input(t("hdl", lang), 20.0, 110.0, float(defaults["hdl"]))
    sbp = st.slider(t("sbp", lang), 90, 220, int(defaults["sbp"]))
    ckd_egfr = st.slider(t("ckd_egfr", lang), 10.0, 130.0, float(defaults["ckd_egfr"]))

    col1, col2 = st.columns(2)
    smoker   = col1.checkbox(t("smoker", lang),   value=defaults["smoker"])
    diabetes = col2.checkbox(t("diabetes", lang), value=defaults["diabetes"])
    ascvd    = col1.checkbox(t("ascvd", lang),    value=defaults["ascvd"])
    fh       = col2.checkbox(t("fh", lang),       value=defaults["fh"])
    intolerant = st.checkbox(t("statin_intolerant", lang), value=defaults["statin_intolerant"])

    lp_a = st.number_input(t("lp_a", lang), 0.0, 400.0, float(defaults["lp_a"]))

tab_calc, tab_dataset = st.tabs([t("tab_calculator", lang), t("tab_dataset", lang)])

with tab_calc:
    if case_explanation:
        with st.expander(t("case_explanation", lang), expanded=True):
            st.markdown(case_explanation)

    # ---------- build patient + run recommendation ----------
    patient = Patient(
        age=age, sex=sex, baseline_ldl=baseline_ldl, smoker=smoker, diabetes=diabetes,
        ascvd=ascvd, fh=fh, ckd_egfr=ckd_egfr, sbp=sbp, total_chol=total_chol, hdl=hdl,
        lp_a=lp_a, statin_intolerant=intolerant,
    )

    result = recommend_step(patient, partial(ldl_predictor.predict_for_patient, bundle))

    # ---------- output ----------
    top = st.columns(3)
    top[0].metric(t("risk_category", lang), risk_label(result["risk"], lang))
    top[1].metric(t("ldl_target", lang), f"< {result['target']:.0f} mg/dL")
    top[2].metric(t("untreated_ldl", lang), f"{patient.baseline_ldl:.0f} mg/dL")

    st.subheader(t("recommended_step", lang))
    st.success(f"➡️  **{step_label(result['chosen_step']['id'], lang)}**")

    st.subheader(t("ladder_title", lang))
    traj = result["trajectory"]
    df = pd.DataFrame([
        {
            t("col_step", lang): step_label(tr["step"]["id"], lang),
            t("col_predicted", lang): tr["predicted_ldl"],
            t("col_viable", lang): tr["viable"],
        }
        for tr in traj
    ])

    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = []
    for tr in traj:
        if not tr["viable"]:
            colors.append("#aaaaaa")
        elif tr["step"]["id"] == result["chosen_step"]["id"]:
            colors.append("#2e7d32")
        elif tr["predicted_ldl"] <= result["target"]:
            colors.append("#a5d6a7")
        else:
            colors.append("#ef5350")
    ax.barh(df[t("col_step", lang)], df[t("col_predicted", lang)], color=colors)
    ax.axvline(
        result["target"], linestyle="--", color="black",
        label=f"{t('target_legend', lang)} {result['target']:.0f}",
    )
    ax.invert_yaxis()
    ax.set_xlabel(t("x_axis", lang))
    ax.legend(loc="lower right")
    st.pyplot(fig)

    with st.expander(t("show_table", lang)):
        st.dataframe(df.style.format({t("col_predicted", lang): "{:.1f}"}), width="stretch")

    st.divider()
    st.caption(t(
        "model_caption", lang,
        mae=bundle["metrics"]["mae"], r2=bundle["metrics"]["r2"], n=bundle["metrics"]["n_test"],
    ))
    st.caption(t("disclaimer", lang))

with tab_dataset:
    st.subheader(t("tab_dataset", lang))
    st.markdown(t("dataset_desc", lang))
    
    if os.path.exists(COHORT_PATH):
        df_cohort = pd.read_csv(COHORT_PATH)
        
        def get_treatment_label(row):
            parts = []
            if row["statin"] == "high":
                parts.append("High Statin")
            elif row["statin"] == "moderate":
                parts.append("Mod Statin")
            if row["ezetimibe"]:
                parts.append("EZE")
            if row["pcsk9"]:
                parts.append("PCSK9i")
            if row["bempedoic"]:
                parts.append("Bempedoic")
            if not parts:
                return "Lifestyle Only"
            return " + ".join(parts)
            
        df_cohort["Treatment"] = df_cohort.apply(get_treatment_label, axis=1)
        st.dataframe(df_cohort, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Baseline vs Post-Treatment LDL-C by Treatment Group**")
            st.scatter_chart(df_cohort, x="baseline_ldl", y="post_ldl", color="Treatment")
            
        with col2:
            st.markdown(t("chart_age", lang))
            age_counts = df_cohort['age'].value_counts().sort_index()
            st.bar_chart(age_counts)
            
    else:
        st.warning(t("dataset_not_found", lang))
