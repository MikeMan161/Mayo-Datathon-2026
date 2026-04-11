import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import roc_auc_score

# -----------------------------
# 1. LOAD CSV DATASET
# -----------------------------
df = pd.read_csv("dummy_aki_dataset.csv")

# -----------------------------
# 2. BASIC CLEANING / ENCODING
# -----------------------------
df["sex"] = df["sex"].map({"M": 1, "F": 0})

# IMPORTANT: sort BEFORE feature/target creation to keep temporal structure clean
df = df.sort_values(["patient_id", "time_hour"]).reset_index(drop=True)

# -----------------------------
# 3. FEATURES / TARGET
# -----------------------------
features = [
    "age", "sex", "creatinine", "lactate",
    "map", "vasopressor", "fluid_balance", "ventilation"
]

X = df[features]
y = df["aki_future"]

# -----------------------------
# 4. TRAIN / TEST SPLIT (BY PATIENT)
# -----------------------------
gss = GroupShuffleSplit(test_size=0.2, n_splits=1, random_state=42)

train_idx, test_idx = next(
    gss.split(df, y, groups=df["patient_id"])
)

# split using SAME dataframe ordering (prevents misalignment bugs)
X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]
y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

# -----------------------------
# 5. HANDLE CLASS IMBALANCE (IMPORTANT FOR AKI)
# -----------------------------
pos = y_train.sum()
neg = len(y_train) - pos
scale_pos_weight = neg / pos if pos > 0 else 1

# -----------------------------
# 6. TRAIN XGBOOST
# -----------------------------
model = xgb.XGBClassifier(
    n_estimators=100,  # good variable to manipulate for overfitting or under fitting
    max_depth=4,  # another good variable
    learning_rate=0.1,  # another good variable
    eval_metric='logloss',
    scale_pos_weight=scale_pos_weight
)

model.fit(X_train, y_train)

train_probs = model.predict_proba(X_train)[:, 1]
train_auc = roc_auc_score(y_train, train_probs)

test_probs = model.predict_proba(X_test)[:, 1]
test_auc = roc_auc_score(y_test, test_probs)

print("\nModel Performance:")
print(f"Train AUC: {train_auc:.3f}")
print(f"Test AUC:  {test_auc:.3f}")
# -----------------------------
# 7. EVALUATE
# -----------------------------
probs = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, probs)

print(f"AUC: {auc:.3f}")

# -----------------------------
# 8. SAVE MODEL
# -----------------------------
model.save_model("aki_xgb_model.json")
print("\nModel saved as aki_xgb_model.json")

# -----------------------------
# 9. CLASS DISTRIBUTION CHECK
# -----------------------------
'''print("\nTrain class distribution:")
print(y_train.value_counts())

print("\nTest class distribution:")
print(y_test.value_counts())'''
