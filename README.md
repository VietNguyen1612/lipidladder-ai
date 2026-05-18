# LipidLadder AI — Topic 3 Demo

ML-augmented clinical decision support for **statin + ezetimibe** stepwise therapy,
based on the **ESC/EAS 2025 Focused Update on Dyslipidaemia Management** (Eur Heart J, ehaf190).

## What it does
1. Takes a patient profile.
2. Classifies risk per ESC/EAS Table 3 and looks up the LDL-C target (Figure 1).
3. A trained `GradientBoostingRegressor` predicts the **post-treatment LDL-C** for each rung of the therapy ladder.
4. Returns the **minimum step** that achieves the target — exactly the stepwise principle from §4 of the guideline.

## Therapy ladder
1. Lifestyle only
2. Moderate-intensity statin
3. High-intensity statin
4. High-intensity statin + ezetimibe
5. + bempedoic acid
6. + PCSK9 inhibitor
7. Quad therapy (max combo)

Reductions calibrated to **Figure 2** of the guideline.

## Layout
```
topic3-lipidladder/
├── app.py                       # Streamlit UI
├── data/synthetic_cohort.py     # generates training data
├── model/ldl_predictor.py       # GradientBoosting regressor
├── engine/ladder.py             # risk stratification + stepwise recommender
├── case_studies.json            # pre-loaded clinical cases
├── requirements.txt
└── README.md
```

## Run

```bash
cd topic3-lipidladder
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# First run trains the model automatically; or pre-train explicitly:
python -m data.synthetic_cohort --n 2000
python -m model.ldl_predictor

streamlit run app.py
```

Educational demo for a course assignment — **not a clinical tool**.
