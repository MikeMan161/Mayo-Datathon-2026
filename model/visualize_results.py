import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# 1. LOAD DATA
# -----------------------------
df = pd.read_csv("daily_predictions.csv")

# Convert predicted risk to numeric
df["predicted_risk"] = df["predicted_risk"].str.replace("%", "").astype(float)

# -----------------------------
# 2. RISK OVER TIME (PER PATIENT)
# -----------------------------
for patient_id in df["stay_id"].unique():
    patient_df = df[df["stay_id"] == patient_id]

    plt.figure()
    plt.plot(patient_df["icu_day"], patient_df["predicted_risk"], marker='o')
    plt.title(f"AKI Risk Over Time (Patient {patient_id})")
    plt.xlabel("ICU Day")
    plt.ylabel("Predicted AKI Risk (%)")
    plt.grid()

    plt.savefig(f"risk_over_time_{patient_id}.png")
    plt.close()

print("Saved: Risk over time plots")

# -----------------------------
# 3. GLOBAL FEATURE IMPORTANCE (SHAP)
# -----------------------------
shap_cols = [col for col in df.columns if col.startswith("shap_")]

# Mean absolute SHAP values
importance = df[shap_cols].abs().mean().sort_values(ascending=False)

plt.figure()
importance.plot(kind="bar")
plt.title("Global Feature Importance (SHAP)")
plt.xlabel("Features")
plt.ylabel("Mean |SHAP Value|")
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("feature_importance_shap.png")
plt.close()

print("Saved: SHAP feature importance")

# -----------------------------
# 4. TOP FEATURES FREQUENCY
# -----------------------------
feature_counts = {}

for row in df["top_features"]:
    features = [f.split(":")[0] for f in row.split("|")]
    for f in features:
        f = f.strip()
        feature_counts[f] = feature_counts.get(f, 0) + 1

feature_counts = pd.Series(feature_counts).sort_values(ascending=False)

plt.figure()
feature_counts.plot(kind="bar")
plt.title("Most Frequently Important Features")
plt.xlabel("Feature")
plt.ylabel("Count")
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("top_feature_frequency.png")
plt.close()

print("Saved: Top feature frequency")

# -----------------------------
# 5. RISK vs OLIGURIA / ANURIA
# -----------------------------
plt.figure()
df.boxplot(column="predicted_risk", by="flag_oliguria_24h")
plt.title("Risk vs Oliguria")
plt.suptitle("")
plt.xlabel("Oliguria (0 = No, 1 = Yes)")
plt.ylabel("Predicted Risk (%)")

plt.savefig("risk_vs_oliguria.png")
plt.close()

plt.figure()
df.boxplot(column="predicted_risk", by="flag_anuria_24h")
plt.title("Risk vs Anuria")
plt.suptitle("")
plt.xlabel("Anuria (0 = No, 1 = Yes)")
plt.ylabel("Predicted Risk (%)")

plt.savefig("risk_vs_anuria.png")
plt.close()

print("Saved: Risk vs clinical flags")

# -----------------------------
# 6. RISK DISTRIBUTION
# -----------------------------
plt.figure()
plt.hist(df["predicted_risk"], bins=20)
plt.title("Distribution of Predicted AKI Risk")
plt.xlabel("Risk (%)")
plt.ylabel("Frequency")

plt.savefig("risk_distribution.png")
plt.close()

print("Saved: Risk distribution")

print("\nAll visualizations saved successfully.")
