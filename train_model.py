import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import roc_auc_score, classification_report

# -----------------------------
# 1. LOAD DATA
# -----------------------------
df = pd.read_csv("cleaned_aki_dataset.csv")

# -----------------------------
# 2. BASIC CLEANING
# -----------------------------
df["gender"] = df["gender"].map({"M": 1, "F": 0})
df = df.sort_values(["stay_id", "icu_day"]).reset_index(drop=True)
df = df.fillna(df.median(numeric_only=True))

# -----------------------------
# 3. TARGET
# -----------------------------
df["aki_next_24h"] = df.groupby("stay_id")["aki_today"].shift(-1)
df = df.dropna(subset=["aki_next_24h"])

# -----------------------------
# 4. FEATURES
# -----------------------------
features = [
    "age",
    "gender",
    "cci_score",
    "baseline_weight_kg",
    "is_on_vasopressor",
    "num_distinct_vasopressors",
    "is_on_nephrotoxic",
    "num_distinct_nephrotoxins",
    "uo_rate_ml_kg_hr",
    "flag_oliguria_24h",
    "flag_anuria_24h"
]

X = df[features]
y = df["aki_next_24h"]

# -----------------------------
# 5. TRAIN / TEST SPLIT
# -----------------------------
gss = GroupShuffleSplit(test_size=0.3, n_splits=1, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=df["stay_id"]))

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]
y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

# -----------------------------
# 6. CLASS IMBALANCE
# -----------------------------
pos = y_train.sum()
neg = len(y_train) - pos
scale_pos_weight = neg / pos if pos > 0 else 1

# -----------------------------
# 7. STRONGER REGULARIZED MODEL
# -----------------------------
model = xgb.XGBClassifier(
    n_estimators=500,          # allow early stopping to choose
    max_depth=1,                # 🔥 EVEN SIMPLER MODEL
    learning_rate=0.01,         # slower learning
    early_stopping_rounds=50,

    subsample=0.6,              # more randomness
    colsample_bytree=0.6,

    min_child_weight=10,        # harder to split
    gamma=1.0,                  # penalize splits more

    reg_alpha=1.0,              # stronger L1
    reg_lambda=5.0,             # stronger L2

    eval_metric="auc",          # better metric for imbalance
    scale_pos_weight=scale_pos_weight,
    random_state=42
)

# -----------------------------
# 8. TRAIN WITH EARLY STOPPING
# -----------------------------
model.fit(
    X_train, y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=True
)

# -----------------------------
# 9. EVALUATION
# -----------------------------
train_probs = model.predict_proba(X_train)[:, 1]
test_probs = model.predict_proba(X_test)[:, 1]

train_auc = roc_auc_score(y_train, train_probs)
test_auc = roc_auc_score(y_test, test_probs)

print("\nModel Performance:")
print(f"Train AUC: {train_auc:.3f}")
print(f"Test AUC:  {test_auc:.3f}")

preds = (test_probs > 0.5).astype(int)

print("\nClassification Report:")
print(classification_report(y_test, preds))

# -----------------------------
# 10. SAVE MODEL
# -----------------------------
model.save_model("aki_xgb_model.json")
print("\nModel saved as aki_xgb_model.json")
