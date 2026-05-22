"""Translation strings for LipidLadder AI (English / Vietnamese)."""
from __future__ import annotations

LANGUAGES = {"English": "en", "Tiếng Việt": "vi"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ---- App chrome ----
    "app_title": {
        "en": "💊 LipidLadder AI",
        "vi": "💊 LipidLadder AI",
    },
    "app_caption": {
        "en": "ESC/EAS 2025 stepwise lipid-lowering recommender — statin + ezetimibe demo",
        "vi": "Công cụ gợi ý điều trị hạ lipid theo bậc — ESC/EAS 2025 (statin + ezetimibe)",
    },
    "language": {"en": "Language", "vi": "Ngôn ngữ"},
    "tab_calculator": {"en": "Clinical Calculator", "vi": "Máy tính lâm sàng"},
    "tab_dataset": {"en": "Dataset Explorer", "vi": "Khám phá dữ liệu"},

    # ---- Sidebar ----
    "patient_input": {"en": "Patient input", "vi": "Thông tin bệnh nhân"},
    "preloaded_case": {"en": "Pre-loaded case", "vi": "Ca lâm sàng có sẵn"},
    "blank": {"en": "(blank)", "vi": "(trống)"},
    "age": {"en": "Age", "vi": "Tuổi"},
    "sex": {"en": "Sex", "vi": "Giới tính"},
    "sex_M": {"en": "M", "vi": "Nam"},
    "sex_F": {"en": "F", "vi": "Nữ"},
    "baseline_ldl": {"en": "Untreated LDL-C (mg/dL)", "vi": "LDL-C nền (mg/dL)"},
    "total_chol": {"en": "Total cholesterol (mg/dL)", "vi": "Cholesterol toàn phần (mg/dL)"},
    "hdl": {"en": "HDL-C (mg/dL)", "vi": "HDL-C (mg/dL)"},
    "sbp": {"en": "Systolic BP", "vi": "Huyết áp tâm thu"},
    "ckd_egfr": {"en": "eGFR (mL/min/1.73m²)", "vi": "eGFR (mL/phút/1.73m²)"},
    "smoker": {"en": "Smoker", "vi": "Hút thuốc"},
    "diabetes": {"en": "Diabetes", "vi": "Đái tháo đường"},
    "ascvd": {"en": "ASCVD", "vi": "Bệnh tim mạch xơ vữa (ASCVD)"},
    "fh": {"en": "FH", "vi": "Tăng cholesterol gia đình (FH)"},
    "statin_intolerant": {"en": "Statin intolerant", "vi": "Không dung nạp statin"},
    "lp_a": {"en": "Lp(a) (nmol/L)", "vi": "Lp(a) (nmol/L)"},

    # ---- Output ----
    "risk_category": {"en": "Risk category", "vi": "Phân tầng nguy cơ"},
    "ldl_target": {"en": "LDL-C target", "vi": "Mục tiêu LDL-C"},
    "untreated_ldl": {"en": "Untreated LDL", "vi": "LDL-C nền"},
    "recommended_step": {"en": "Recommended therapy step", "vi": "Bậc điều trị khuyến nghị"},
    "ladder_title": {
        "en": "Stepwise ladder — predicted LDL-C at each rung",
        "vi": "Thang điều trị — LDL-C dự đoán ở mỗi bậc",
    },
    "x_axis": {
        "en": "Predicted post-treatment LDL-C (mg/dL)",
        "vi": "LDL-C dự đoán sau điều trị (mg/dL)",
    },
    "target_legend": {"en": "Target <", "vi": "Mục tiêu <"},
    "show_table": {"en": "Show numeric table", "vi": "Hiển thị bảng số liệu"},
    "col_step": {"en": "Step", "vi": "Bậc"},
    "col_predicted": {"en": "Predicted LDL", "vi": "LDL dự đoán"},
    "col_viable": {"en": "Viable", "vi": "Khả dụng"},

    "model_caption": {
        "en": "Model: GradientBoostingRegressor | MAE = {mae:.2f} mg/dL · R² = {r2:.3f} (n_test = {n})",
        "vi": "Mô hình: GradientBoostingRegressor | MAE = {mae:.2f} mg/dL · R² = {r2:.3f} (n_test = {n})",
    },
    "disclaimer": {
        "en": "Educational demo for the ESC/EAS 2025 Focused Update — not for clinical use.",
        "vi": "Demo phục vụ học tập theo ESC/EAS 2025 — không dùng cho lâm sàng.",
    },

    # ---- Dataset Explorer ----
    "dataset_desc": {
        "en": "This cohort dataset contains 2,000 synthetic patient records (8,000 observations across therapeutic steps) simulating lipid-lowering responses under various regimens (statin, ezetimibe, PCSK9 inhibitors, and bempedoic acid) based on the ESC/EAS 2025 guidelines.",
        "vi": "Tập dữ liệu này chứa thông tin của 2.000 hồ sơ bệnh nhân giả lập (8.000 lượt quan sát qua các bậc điều trị) mô phỏng phản ứng hạ lipid dưới các phác đồ khác nhau (statin, ezetimibe, chất ức chế PCSK9, và axit bempedoic) dựa trên hướng dẫn ESC/EAS 2025.",
    },
    "chart_age": {
        "en": "**Age Distribution in the Cohort**",
        "vi": "**Phân bố độ tuổi trong tập dữ liệu**",
    },
    "dataset_not_found": {
        "en": "Cohort dataset file not found. It will be generated automatically when you load the Clinical Calculator.",
        "vi": "Không tìm thấy file dữ liệu đoàn hệ. Tập dữ liệu sẽ tự động được tạo khi bạn mở Máy tính lâm sàng.",
    },

    # ---- Risk categories ----
    "risk_low": {"en": "LOW", "vi": "THẤP"},
    "risk_moderate": {"en": "MODERATE", "vi": "TRUNG BÌNH"},
    "risk_high": {"en": "HIGH", "vi": "CAO"},
    "risk_very_high": {"en": "VERY HIGH", "vi": "RẤT CAO"},

    # ---- Therapy step labels (keyed by step id) ----
    "step_lifestyle": {
        "en": "Lifestyle only",
        "vi": "Chỉ thay đổi lối sống",
    },
    "step_moderate_statin": {
        "en": "Moderate-intensity statin",
        "vi": "Statin cường độ trung bình",
    },
    "step_high_statin": {
        "en": "High-intensity statin",
        "vi": "Statin cường độ cao",
    },
    "step_high_statin_eze": {
        "en": "High-intensity statin + ezetimibe",
        "vi": "Statin cường độ cao + ezetimibe",
    },
    "step_high_statin_eze_bemp": {
        "en": "High-intensity statin + EZE + bempedoic acid",
        "vi": "Statin cường độ cao + ezetimibe + acid bempedoic",
    },
    "step_high_statin_eze_pcsk9": {
        "en": "High-intensity statin + EZE + PCSK9 inhibitor",
        "vi": "Statin cường độ cao + ezetimibe + ức chế PCSK9",
    },
    "step_max_combo": {
        "en": "High-intensity statin + EZE + PCSK9i + bempedoic acid",
        "vi": "Statin cường độ cao + ezetimibe + ức chế PCSK9 + acid bempedoic",
    },
}


def t(key: str, lang: str, **fmt) -> str:
    """Look up `key` in language `lang`; format with optional kwargs."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(lang, entry.get("en", key))
    return text.format(**fmt) if fmt else text


def risk_label(risk: str, lang: str) -> str:
    return t(f"risk_{risk}", lang)


def step_label(step_id: str, lang: str) -> str:
    return t(f"step_{step_id}", lang)
