import pandas as pd
import xgboost as xgb
import boto3
import shap


# load the newest data from cloud
def load_latest_data():
    s3 = boto3.client("s3")  # creates a connection to the cloud, s3 = control object

    bucket = "aki-data-bucket"  # s3 storage container (top level folder in AWS)
    key = "daily/new_patient_data.csv"  # exact file path inside the bucket

    s3.download_file(bucket, key, "temp.csv")  # downloads the file from AWS and saves it to "temp.csv"

    return pd.read_csv("temp.csv")

# -----------------------------
# 1. LOAD TRAINED MODEL
# -----------------------------
model = xgb.XGBClassifier()
model.load_model("aki_xgb_model.json")

# -----------------------------
# 2. LOAD NEW DAILY DATA
# -----------------------------
# This file should contain ONLY the latest 24h data
# df_new = load_latest_data()
df_new = pd.read_csv("dummy_aki_dataset.csv")

# -----------------------------
# 3. SAME PREPROCESSING (CRITICAL)
# -----------------------------
df_new["sex"] = df_new["sex"].map({"M": 1, "F": 0})

features = [
    "age", "sex", "creatinine", "lactate",
    "map", "vasopressor", "fluid_balance", "ventilation"
]

X_new = df_new[features]

# -----------------------------
# 4. PREDICT RISK
# -----------------------------
df_new["predicted_risk"] = (model.predict_proba(X_new)[:, 1] * 100).round(1).astype(str) + "%"

# -----------------------------
# 5. EXPLAIN PREDICTIONS (SHAP)
# -----------------------------
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_new)

# convert SHAP values into dataframe
shap_df = pd.DataFrame(shap_values, columns=features)
shap_df = shap_df.add_prefix("shap_")

# merge with original dataframe
df_new = pd.concat([df_new.reset_index(drop=True), shap_df], axis=1)


# helper function to get top contributing features
def get_top_features(shap_row, feature_names, top_n=3):
    importance = list(zip(feature_names, shap_row))
    importance = sorted(importance, key=lambda x: abs(x[1]), reverse=True)
    return importance[:top_n]


# compute top features per prediction
top_features_list = []

for i in range(len(X_new)):
    top_feats = get_top_features(shap_values[i], features)

    # format into clean readable string
    formatted = [
        f"{name}: {float(value):+.2f}"   # + shows positive/negative impact
        for name, value in top_feats
    ]

    top_features_list.append(" | ".join(formatted))

df_new["top_features"] = top_features_list

# -----------------------------
# 6. OUTPUT RESULTS
# -----------------------------
print("\nDaily AKI Risk Predictions:")
print(df_new[["patient_id", "time_hour", "predicted_risk", "top_features"]])

# Optional: save results
df_new.to_csv("daily_predictions.csv", index=False)

print("\nPredictions saved to daily_predictions.csv")