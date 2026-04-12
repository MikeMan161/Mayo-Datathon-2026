import pandas as pd

# -----------------------------
# 1. LOAD RAW DATASET
# -----------------------------
df = pd.read_csv("FinalQueryResult.csv")

print("Original shape:", df.shape)

# -----------------------------
# 2. SELECT FEATURES + TARGET
# -----------------------------
selected_columns = [
    "stay_id",            # identifier (for grouping)
    "icu_day",            # time tracking ONLY (not a feature)
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
    "flag_anuria_24h",
    "aki_today"           # target
]

df = df[selected_columns]

print("After column selection:", df.shape)

# -----------------------------
# 3. CLEAN / ENCODE DATA
# -----------------------------

# Encode gender
df["gender"] = df["gender"].map({"M": 1, "F": 0})

# Convert boolean-like columns to int (if needed)
bool_cols = [
    "is_on_vasopressor",
    "is_on_nephrotoxic",
    "flag_oliguria_24h"
]

for col in bool_cols:
    df[col] = df[col].astype(int)

# -----------------------------
# 4. HANDLE MISSING VALUES
# -----------------------------
df = df.fillna(df.median(numeric_only=True))

# -----------------------------
# 5. SORT (IMPORTANT FOR TIME SERIES)
# -----------------------------
df = df.sort_values(["stay_id", "icu_day"]).reset_index(drop=True)

# -----------------------------
# 6. FINAL CHECK
# -----------------------------
print("\nCleaned dataset preview:")
print(df.head())

print("\nFinal shape:", df.shape)
print("\nMissing values per column:")
print(df.isnull().sum())

# -----------------------------
# 7. SAVE CLEAN DATASET
# -----------------------------
df.to_csv("cleaned_aki_dataset.csv", index=False)

print("\nCleaned dataset saved as cleaned_aki_dataset.csv")