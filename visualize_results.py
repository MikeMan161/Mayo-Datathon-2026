import pandas as pd
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# 1. LOAD CSV DATASET
# -----------------------------
df = pd.read_csv("dummy_aki_dataset.csv")

# -----------------------------
# 2. BASIC CLEANING / ENCODING
# -----------------------------
df["sex"] = df["sex"].map({"M": 1, "F": 0})

# -----------------------------
# 3. FEATURES / TARGET
# -----------------------------
features = [
    "age", "sex", "creatinine", "lactate",
    "map", "vasopressor", "fluid_balance", "ventilation"
]

X = df[features]

# -----------------------------
# 11. LOAD TRAINED MODEL
# -----------------------------
model = xgb.XGBClassifier()
model.load_model("aki_xgb_model.json")

# -----------------------------
# 7. PREDICT RISK EVERY 24H
# -----------------------------
df["predicted_risk"] = model.predict_proba(X)[:, 1]

# =========================================================
# 1. CLEAN GLOBAL FEATURE IMPORTANCE (REPLACES SHAP SUMMARY)
# =========================================================
importance = model.feature_importances_
sorted_idx = np.argsort(importance)

plt.figure(figsize=(8, 5))
plt.barh(np.array(features)[sorted_idx], importance[sorted_idx])
plt.title("Feature Importance (XGBoost Global View)")
plt.xlabel("Importance Score")
plt.tight_layout()
plt.show()

# =========================================================
# 2. SINGLE PATIENT STORY (CLEAN LINE PLOT)
# =========================================================
patient_id = 1001
patient_df = df[df["patient_id"] == patient_id]

plt.figure(figsize=(8, 5))
plt.plot(patient_df["time_hour"], patient_df["predicted_risk"], marker="o")

plt.title(f"AKI Risk Progression Over Time (Patient {patient_id})")
plt.xlabel("Time (hours)")
plt.ylabel("Predicted AKI Risk")
plt.ylim(0, 1)
plt.grid(True, alpha=0.3)

plt.show()

# =========================================================
# 3. COMPARE 3 PATIENT TYPES (MORE INSIGHTFUL THAN ALL LINES)
# =========================================================
selected_patients = [1001, 1006, 1017]

plt.figure(figsize=(8, 5))

for pid in selected_patients:
    temp = df[df["patient_id"] == pid]
    plt.plot(temp["time_hour"], temp["predicted_risk"], marker="o", label=f"Patient {pid}")

plt.title("AKI Risk Trajectories (Selected Patients)")
plt.xlabel("Time (hours)")
plt.ylabel("Predicted AKI Risk")
plt.ylim(0, 1)
plt.legend()
plt.grid(True, alpha=0.3)

plt.show()

# =========================================================
# 4. SHAP (ONLY FOR INTERPRETATION — NOT PRIMARY VISUAL)
# =========================================================
explainer = shap.Explainer(model)
shap_values = explainer(X)

# Keep SHAP but make it secondary
shap.summary_plot(shap_values, X)

# =========================================================
# 5. SINGLE EXPLANATION (CLEANED)
# =========================================================
patient_example = df[df["patient_id"] == 1001]

row_idx = patient_example[patient_example["time_hour"] == 48].index[0]

print("\nSHAP explanation for Patient 1001 at 48h:")
shap.plots.waterfall(shap_values[row_idx])


