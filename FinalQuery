-- =============================================================================
-- FINAL INTEGRATED MASTER LANDMARK QUERY
-- Optimized Column Naming & Full UO + Pressor + Nephrotoxin Integration
-- =============================================================================

WITH lung_cancer AS (
    SELECT DISTINCT subject_id, hadm_id
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE (icd_version = 10 AND icd_code IN ('C3400','C3401','C3402','C3410','C3411','C3412','C342','C3430','C3431','C3432','C3480','C3481','C3482','C3490','C3491','C3492', 'C7800','C7801','C7802','C4650','C4651','C4652','C7A090'))
       OR (icd_version = 9 AND icd_code IN ('1620','1622','1623','1624','1625','1628','1629','1970','1764'))
),
aki_on_admission AS (
    SELECT DISTINCT hadm_id FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE seq_num = 1 AND ((icd_version = 9 AND icd_code IN ('584','5845','5846','5847','5848','5849')) OR (icd_version = 10 AND icd_code IN ('N17','N170','N171','N172','N178','N179')))
),
exclude_renal AS (
    SELECT DISTINCT subject_id FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE icd_code IN ('N184','N185','N186','5854','5855','5856','V4511','V4512','V451') OR icd_code LIKE 'Z992%'
),
remission_only AS (
    SELECT hadm_id FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE (icd_version = 10 AND icd_code LIKE 'Z85%') OR (icd_version = 9 AND icd_code LIKE 'V10%')
    EXCEPT DISTINCT SELECT hadm_id FROM lung_cancer
),
first_icu AS (
    SELECT icu.subject_id, icu.hadm_id, icu.stay_id, icu.intime, icu.outtime, icu.los,
           CEIL(icu.los) AS n_icu_days,
           ROW_NUMBER() OVER (PARTITION BY icu.subject_id ORDER BY icu.intime) AS rn
    FROM `physionet-data.mimiciv_3_1_icu.icustays` icu
    INNER JOIN lung_cancer lc ON icu.hadm_id = lc.hadm_id
    WHERE icu.hadm_id NOT IN (SELECT hadm_id FROM aki_on_admission)
      AND icu.subject_id NOT IN (SELECT subject_id FROM exclude_renal)
      AND icu.hadm_id NOT IN (SELECT hadm_id FROM remission_only)
      AND icu.los >= 1
),
cci_comorbidities AS (
    SELECT hadm_id,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'I21%' OR icd_code LIKE 'I22%' OR icd_code = 'I252')) OR (icd_version = 9 AND (icd_code LIKE '410%' OR icd_code LIKE '412%')) THEN 1 ELSE 0 END) AS mi,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'I099' OR icd_code LIKE 'I110' OR icd_code LIKE 'I50%' OR icd_code LIKE 'P290')) OR (icd_version = 9 AND (icd_code LIKE '428%')) THEN 1 ELSE 0 END) AS chf,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'I70%' OR icd_code LIKE 'I71%')) OR (icd_version = 9 AND (icd_code LIKE '440%' OR icd_code LIKE '441%')) THEN 1 ELSE 0 END) AS pvd,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code BETWEEN 'I60' AND 'I69')) OR (icd_version = 9 AND (icd_code LIKE '430%' OR icd_code LIKE '431%' OR icd_code LIKE '438%')) THEN 1 ELSE 0 END) AS cvd,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'F00%' OR icd_code LIKE 'G30%')) OR (icd_version = 9 AND (icd_code LIKE '290%')) THEN 1 ELSE 0 END) AS dementia,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code BETWEEN 'J40' AND 'J47')) OR (icd_version = 9 AND (icd_code BETWEEN '4900' AND '5059')) THEN 1 ELSE 0 END) AS cpd,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'M05%' OR icd_code LIKE 'M06%' OR icd_code LIKE 'M32%')) OR (icd_version = 9 AND (icd_code LIKE '7140%' OR icd_code LIKE '7100%')) THEN 1 ELSE 0 END) AS rheumatic,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'K25%' OR icd_code LIKE 'K26%')) OR (icd_version = 9 AND (icd_code LIKE '531%' OR icd_code LIKE '532%')) THEN 1 ELSE 0 END) AS pud,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'B18%' OR icd_code LIKE 'K70%' OR icd_code LIKE 'K74%')) OR (icd_version = 9 AND (icd_code LIKE '571%')) THEN 1 ELSE 0 END) AS liver_mild,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'E100%' OR icd_code LIKE 'E109%' OR icd_code LIKE 'E119%')) OR (icd_version = 9 AND (icd_code LIKE '2500%')) THEN 1 ELSE 0 END) AS dm_no_comp,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'E102%' OR icd_code LIKE 'E112%' OR icd_code LIKE 'E114%')) OR (icd_version = 9 AND (icd_code LIKE '2504%' OR icd_code LIKE '2506%')) THEN 1 ELSE 0 END) AS dm_comp,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'G81%' OR icd_code LIKE 'G82%')) OR (icd_version = 9 AND (icd_code LIKE '3420%' OR icd_code LIKE '3441%')) THEN 1 ELSE 0 END) AS hemiplegia,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'N18%')) OR (icd_version = 9 AND (icd_code LIKE '585%')) THEN 1 ELSE 0 END) AS renal,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code BETWEEN 'C00' AND 'C76')) OR (icd_version = 9 AND (icd_code BETWEEN '140' AND '172' OR icd_code BETWEEN '174' AND '195')) THEN 1 ELSE 0 END) AS malignancy,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'I850%' OR icd_code LIKE 'K72%')) OR (icd_version = 9 AND (icd_code LIKE '4560%' OR icd_code LIKE '5722%')) THEN 1 ELSE 0 END) AS liver_severe,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code BETWEEN 'C77' AND 'C80')) OR (icd_version = 9 AND (icd_code BETWEEN '196' AND '199')) THEN 1 ELSE 0 END) AS metastatic,
        MAX(CASE WHEN (icd_version = 10 AND (icd_code LIKE 'B20%')) OR (icd_version = 9 AND (icd_code LIKE '042%')) THEN 1 ELSE 0 END) AS aids
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd` GROUP BY hadm_id
),
patient_weight AS (
    SELECT ce.stay_id, AVG(ce.valuenum) AS weight_kg
    FROM `physionet-data.mimiciv_3_1_icu.chartevents` ce
    WHERE ce.itemid = 226512 AND ce.valuenum > 20 AND ce.valuenum < 300
    GROUP BY ce.stay_id
),
static_metrics AS (
    SELECT 
        fi.stay_id, (p.anchor_age + (EXTRACT(YEAR FROM a.admittime) - p.anchor_year)) AS age, p.gender, a.race, a.hospital_expire_flag,
        (SELECT MIN(le.valuenum) FROM `physionet-data.mimiciv_3_1_hosp.labevents` le WHERE le.hadm_id = fi.hadm_id AND le.itemid = 50912 AND le.valuenum > 0 AND le.charttime BETWEEN DATETIME_SUB(fi.intime, INTERVAL 7 DAY) AND DATETIME_ADD(fi.intime, INTERVAL 6 HOUR)) AS baseline_creatinine,
        (cc.mi + cc.chf + cc.pvd + cc.cvd + cc.dementia + cc.cpd + cc.rheumatic + cc.pud + (CASE WHEN cc.liver_severe = 1 THEN 0 ELSE cc.liver_mild END) + (CASE WHEN cc.dm_comp = 1 THEN 0 ELSE cc.dm_no_comp END) + 2*(cc.dm_comp + cc.hemiplegia + cc.renal + cc.malignancy) + 3*cc.liver_severe + 6*(cc.metastatic + cc.aids)) AS cci_score,
        COALESCE(pw.weight_kg, 80.0) AS baseline_weight_kg
    FROM first_icu fi
    INNER JOIN `physionet-data.mimiciv_3_1_hosp.patients` p ON fi.subject_id = p.subject_id
    INNER JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a ON fi.hadm_id = a.hadm_id
    LEFT JOIN cci_comorbidities cc ON fi.hadm_id = cc.hadm_id
    LEFT JOIN patient_weight pw ON fi.stay_id = pw.stay_id
    WHERE fi.rn = 1
),
expanded AS (
    SELECT fi.subject_id, fi.hadm_id, fi.stay_id, fi.intime, fi.outtime, fi.los, fi.n_icu_days, 
        sm.age, sm.gender, sm.race, sm.baseline_creatinine, sm.cci_score, sm.baseline_weight_kg,
        icu_day,
        DATETIME_ADD(fi.intime, INTERVAL (icu_day - 1) DAY) AS day_start,
        DATETIME_ADD(fi.intime, INTERVAL icu_day DAY) AS day_end_full
    FROM first_icu fi
    JOIN static_metrics sm ON fi.stay_id = sm.stay_id
    CROSS JOIN UNNEST(GENERATE_ARRAY(1, CAST(fi.n_icu_days AS INT64))) AS icu_day
),
daily_metrics AS (
    SELECT e.stay_id, e.icu_day,
        MAX(le.valuenum) AS max_creatinine_today,
        -- URINE OUTPUT (Aggregated from teammate's logic)
        SUM(oe.value) AS total_uo_ml_today,
        -- VASOPRESSOR FLAGS & COUNTS
        MAX(CASE WHEN ie_p.itemid IN (221906, 221289, 222315, 221662, 221749, 229617) THEN 1 ELSE 0 END) AS is_on_vasopressor,
        COUNT(DISTINCT CASE WHEN ie_p.itemid IN (221906, 221289, 222315, 221662, 221749, 229617) THEN ie_p.itemid END) AS num_distinct_vasopressors,
        -- NEPHROTOXIC FLAGS & COUNTS
        MAX(CASE WHEN (LOWER(rx.drug) LIKE '%vancomycin%' OR LOWER(rx.drug) LIKE '%cisplatin%' OR LOWER(rx.drug) LIKE '%gentamicin%') THEN 1 ELSE 0 END) AS is_on_nephrotoxic,
        COUNT(DISTINCT CASE WHEN (LOWER(rx.drug) LIKE '%vancomycin%' OR LOWER(rx.drug) LIKE '%cisplatin%' OR LOWER(rx.drug) LIKE '%gentamicin%') THEN rx.drug END) AS num_distinct_nephrotoxins
    FROM expanded e
    LEFT JOIN `physionet-data.mimiciv_3_1_hosp.labevents` le ON e.hadm_id = le.hadm_id AND le.itemid = 50912 AND le.charttime >= e.day_start AND le.charttime < e.day_end_full
    LEFT JOIN `physionet-data.mimiciv_3_1_icu.inputevents` ie_p ON e.stay_id = ie_p.stay_id AND ie_p.starttime >= e.day_start AND ie_p.starttime < e.day_end_full
    LEFT JOIN `physionet-data.mimiciv_3_1_hosp.prescriptions` rx ON e.hadm_id = rx.hadm_id AND rx.starttime >= e.day_start AND rx.starttime < e.day_end_full
    LEFT JOIN `physionet-data.mimiciv_3_1_icu.outputevents` oe ON e.stay_id = oe.stay_id AND oe.itemid IN (226559,226560,226561,226563,226564,226565,226567,226557) AND oe.charttime >= e.day_start AND oe.charttime < e.day_end_full
    GROUP BY e.stay_id, e.icu_day
)

SELECT * FROM (
    SELECT e.*, 
        -- Vasopressor & Nephrotoxin Summary
        dm.is_on_vasopressor, dm.num_distinct_vasopressors,
        dm.is_on_nephrotoxic, dm.num_distinct_nephrotoxins,
        -- Urinary Output Detailed Labels
        dm.total_uo_ml_today,
        ROUND(SAFE_DIVIDE(dm.total_uo_ml_today, e.baseline_weight_kg * 24.0), 3) AS uo_rate_ml_kg_hr,
        CASE WHEN SAFE_DIVIDE(dm.total_uo_ml_today, e.baseline_weight_kg * 24.0) < 0.5 THEN 1 ELSE 0 END AS flag_oliguria_24h,
        CASE WHEN SAFE_DIVIDE(dm.total_uo_ml_today, e.baseline_weight_kg * 24.0) < 0.3 THEN 1 ELSE 0 END AS flag_severe_oliguria_24h,
        CASE WHEN dm.total_uo_ml_today < 100 THEN 1 ELSE 0 END AS flag_anuria_24h,
        -- Renal Outcome
        dm.max_creatinine_today,
        CASE WHEN dm.max_creatinine_today >= 2 * e.baseline_creatinine THEN 1 ELSE 0 END AS aki_today,
        COALESCE(MAX(CASE WHEN dm.max_creatinine_today >= 2 * e.baseline_creatinine THEN 1 ELSE 0 END) OVER (PARTITION BY e.stay_id ORDER BY e.icu_day ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0) AS had_aki_before
    FROM expanded e
    LEFT JOIN daily_metrics dm ON e.stay_id = dm.stay_id AND e.icu_day = dm.icu_day
) WHERE had_aki_before = 0 AND baseline_creatinine IS NOT NULL
ORDER BY subject_id, stay_id, icu_day;
