# Predicting Severe Acute Kidney Injury (AKIN Stage ≥2) in Hospitalized Lung Cancer Patients

**Mayo Clinic Datathon 2026**

## Research Question

Among hospitalized patients with lung cancer, can a clinical risk model accurately predict the development of severe acute kidney injury (AKIN Stage ≥2) within the next 24 hours?

## Overview

Acute kidney injury (AKI) is a serious and common complication in hospitalized cancer patients, associated with increased mortality, prolonged ICU stays, and higher healthcare costs. This project builds a rolling 24-hour AKI onset prediction model for lung cancer ICU patients using real-world clinical data from the MIMIC-IV database.

We used BigQuery SQL to extract and engineer a longitudinal, per-ICU-day dataset tracking clinical features including vasopressor use, nephrotoxin exposure, urine output, and serum creatinine. That dataset was then used to train an XGBoost classifier to predict whether a patient will develop AKIN Stage ≥2 AKI within the following 24 hours.

## Repository Structure

```
├── queries/                        # BigQuery SQL scripts for data extraction
│   ├── FinalQuery.sql              # Primary query — full day-by-day ICU feature dataset (FINAL)
│   ├── AKIquery.sql                # Exploratory: identifies cancer patients with KDIGO Stage 2+ AKI
│   ├── CancerTypesQuery.sql        # Exploratory: breakdown of cancer types among AKI patients
│   ├── totalLungPatients.sql       # Exploratory: lung cancer cohort stratified by hospital LOS
│   └── M_Variables.sql             # Exploratory: patient-level variables (BMI, demographics, CCI)
│
├── data/
│   ├── FinalQueryResult.csv        # Primary dataset — output of FinalQuery.sql
│   ├── cleaned_aki_dataset.csv     # Cleaned/feature-selected dataset — output of model/clean_dataset.py
│   └── exploratory/                # Intermediate CSVs from earlier query iterations (not used in final model)
│       ├── combinedquery.csv
│       ├── dummy_aki_dataset.csv
│       └── dummy_aki_dataset2.csv
│
├── model/
│   ├── clean_dataset.py            # Cleans FinalQueryResult.csv → cleaned_aki_dataset.csv
│   ├── train_model.py              # Trains XGBoost classifier, saves aki_xgb_model.json
│   ├── predict_daily_risk.py       # Loads trained model, scores new daily patient data
│   └── visualize_results.py        # Plots per-patient AKI risk trajectories over ICU stay
│
└── README.md
```

## Data

**Source:** [MIMIC-IV v3.1](https://physionet.org/content/mimiciv/3.1/) via PhysioNet / Google BigQuery

**Cohort:** Adult patients (≥18 years) with lung cancer identified using ICD-9 (162.x) and ICD-10 (C34.x) codes, including metastatic lung malignancies.

**Exclusion criteria:**
- AKI present at admission (ICD codes in first diagnosis position)
- Cancer in remission
- Advanced CKD (Stage 5) or end-stage renal disease at admission

**AKI Definition:** ≥2-fold increase in serum creatinine from baseline during hospitalization (KDIGO / AKIN Stage ≥2).

**Baseline creatinine:** First available value within 24 hours of admission.

> ⚠️ **Note:** `data/exploratory/` contains intermediate CSVs produced during early query development and schema refinement. These files are **not** used in the final model pipeline and are retained for reference only.

## Clinical Features

The model uses a mix of static and daily time-varying features:

| Type | Feature | Description |
|---|---|---|
| Static | `age`, `gender`, `race` | Demographics at admission |
| Static | `cci_score` | Charlson Comorbidity Index |
| Static | `baseline_weight_kg`, `baseline_creatinine` | Admission values |
| Daily | `is_on_vasopressor`, `num_distinct_vasopressors` | Hemodynamic instability |
| Daily | `is_on_nephrotoxic`, `num_distinct_nephrotoxins` | Nephrotoxin exposure count |
| Daily | `uo_rate_ml_kg_hr` | Urine output rate |
| Daily | `flag_oliguria_24h`, `flag_anuria_24h` | Urine output severity flags |
| Target | `aki_today` (shifted +1 day) | AKI onset within next 24 hours |

## Model Pipeline

1. **Extract** — Run `queries/FinalQuery.sql` in BigQuery against MIMIC-IV to produce `data/FinalQueryResult.csv`
2. **Clean** — Run `model/clean_dataset.py` to select features and produce `data/cleaned_aki_dataset.csv`
3. **Train** — Run `model/train_model.py` to train the XGBoost classifier and save `aki_xgb_model.json`
4. **Predict** — Run `model/predict_daily_risk.py` to score new daily patient data using the saved model
5. **Visualize** — Run `model/visualize_results.py` to generate per-patient AKI risk trajectory plots

## Methods Summary

Patients were identified from MIMIC-IV using ICD-9 and ICD-10 lung cancer diagnosis codes. For each patient, a day-by-day ICU record was constructed tracking clinical features across all categories above. The label `aki_next_24h` was derived by shifting `aki_today` forward one day per patient stay.

The model is an XGBoost binary classifier trained with group-based train/test split (grouped by `stay_id`) to prevent data leakage across a patient’s ICU days. Class imbalance was handled via `scale_pos_weight`. Performance was evaluated using AUROC and classification report.

## Data Access

MIMIC-IV requires credentialed access through PhysioNet. To reproduce the SQL extractions, you will need a PhysioNet account with MIMIC-IV access and a connected Google BigQuery project.

- PhysioNet: https://physionet.org/
- MIMIC-IV: https://physionet.org/content/mimiciv/3.1/
