# LipidLadder AI — Demo Parameter Reference

The "demo" is the Streamlit app (`app.py`). All inputs feed into a `Patient` dataclass (`engine/ladder.py:24`), which drives risk classification and the stepwise recommender.

## Patient input parameters (sidebar)

| Param | Type / range | Default | Meaning & where it's used |
|---|---|---|---|
| **age** | int, 30–90 | 55 | Used in SCORE2-like risk score `(age-40)*0.15` (`ladder.py:62`); also a "very_high" trigger when diabetic & age>40. |
| **sex** | "M" / "F" | "M" | Adds +1.5 to risk score if male (`ladder.py:67`). |
| **baseline_ldl** | float, 50–350 mg/dL | 150 | Untreated LDL-C. Triggers "high" risk if ≥190; "very_high" via diabetes branch if ≥130; contributes `(LDL-100)*0.02` to score. Also the starting point that the GradientBoosting model reduces. |
| **total_chol** | float, 100–450 mg/dL | 220 | Triggers "high" risk if ≥310. |
| **hdl** | float, 20–110 mg/dL | 50 | Stored on Patient but not used by `classify_risk` — passed to the LDL predictor as a feature. |
| **sbp** | int, 90–220 mmHg | 130 | Triggers "high" if ≥180, "very_high" via diabetes/FH branches if ≥140; contributes `(sbp-120)*0.05` to score. |
| **ckd_egfr** | float, 10–130 mL/min/1.73m² | 90 | <30 → very_high; 30–60 → high (`ladder.py:48,57`). |
| **smoker** | bool | False | +2 to score; also a very_high modifier with diabetes or FH. |
| **diabetes** | bool | False | +3 to score; with age>40 and one risk factor → very_high. |
| **ascvd** | bool | False | Always → very_high (secondary prevention). |
| **fh** | bool | False | Familial hypercholesterolaemia → at minimum "high"; → "very_high" with ASCVD/smoker/SBP≥140. |
| **lp_a** | float, 0–400 nmol/L | 20 | +1 to score if ≥105 (Box 1 Lp(a) modifier). |
| **statin_intolerant** | bool | False | In `recommend_step`, marks statin-only rungs as non-viable so the ladder skips to ezetimibe/PCSK9-containing steps (`ladder.py:100`). |
| **Pre-loaded case** | dropdown | first case | Loads a profile from `case_studies.json` into the defaults above. |

## Derived outputs

- **Risk category** — `classify_risk()` → `low / moderate / high / very_high` (`ladder.py:41`).
- **LDL-C target** — from `ldl_target()`: very_high=55, high=70, moderate=100, low=116 mg/dL (`ladder.py:76`).
- **Trajectory** — predicted LDL at each of the 7 therapy rungs in `THERAPY_STEPS` (`ladder.py:13`).
- **Chosen step** — minimum viable rung where predicted LDL ≤ target; falls back to max combo if none reach target.

## Hidden / non-UI params

- `MODEL_PATH = "model/ldl_model.joblib"`, `COHORT_PATH = "data/cohort.csv"`, `CASES_PATH = "case_studies.json"` (`app.py:18`).
- Training cohort size **2000** in `get_model_bundle()` (`app.py:29`) — also overridable via `python -m data.synthetic_cohort --n 2000`.
- `secondary_prevention` arg on `ldl_target()` exists but is unused (always False from the UI).
- `hdl` and `total_chol` are collected but only `total_chol` affects risk; both are forwarded to the regressor as features.
