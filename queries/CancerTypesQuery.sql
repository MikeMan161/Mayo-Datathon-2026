WITH cancer_patients AS (
  SELECT DISTINCT d.subject_id, d.hadm_id, d.icd_code, d.icd_version
  FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd` d
  JOIN `physionet-data.mimiciv_3_1_hosp.patients` p
    ON d.subject_id = p.subject_id
  WHERE 
    (
      (d.icd_version = 10 AND d.icd_code BETWEEN 'C00' AND 'C96Z'
      AND d.icd_code NOT LIKE 'Z85%')
    )
    OR
    (
      (d.icd_version = 9 
      AND SAFE_CAST(SUBSTR(d.icd_code, 1, 3) AS INT64) BETWEEN 140 AND 208
      AND d.icd_code NOT LIKE 'V10%')
    )
    AND p.anchor_age >= 18
),
baseline_creatinine AS (
  SELECT 
    l.subject_id,
    l.hadm_id,
    MIN(l.valuenum) AS baseline_cr
  FROM `physionet-data.mimiciv_3_1_hosp.labevents` l
  JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a
    ON l.subject_id = a.subject_id AND l.hadm_id = a.hadm_id
  WHERE 
    l.itemid IN (50912, 52546, 51081, 51977, 52024)
    AND l.valuenum > 0
    AND l.charttime BETWEEN a.admittime 
        AND TIMESTAMP_ADD(a.admittime, INTERVAL 24 HOUR)
  GROUP BY l.subject_id, l.hadm_id
),
peak_creatinine AS (
  SELECT 
    l.subject_id,
    l.hadm_id,
    MAX(l.valuenum) AS peak_cr
  FROM `physionet-data.mimiciv_3_1_hosp.labevents` l
  JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a
    ON l.subject_id = a.subject_id AND l.hadm_id = a.hadm_id
  WHERE 
    l.itemid IN (50912, 52546, 51081, 51977, 52024)
    AND l.valuenum > 0
    AND l.charttime BETWEEN a.admittime AND a.dischtime
  GROUP BY l.subject_id, l.hadm_id
),
aki_kdigo_stage2 AS (
  -- Patients who met KDIGO Stage 2: peak >= 2x baseline
  SELECT 
    b.subject_id,
    b.hadm_id
  FROM baseline_creatinine b
  JOIN peak_creatinine p
    ON b.subject_id = p.subject_id AND b.hadm_id = p.hadm_id
  WHERE p.peak_cr >= 2.0 * b.baseline_cr
)

-- JOIN BACK TO GET CANCER TYPE LABELS
-- Count how many KDIGO Stage 2 AKI patients had each cancer code
-- HAVING filters to codes with at least 50 patients for readability
SELECT
  d.icd_code,
  d.icd_version,
  diag.long_title AS cancer_description,
  COUNT(DISTINCT a.hadm_id) AS aki_patient_count
FROM aki_kdigo_stage2 a
JOIN cancer_patients d
  ON a.subject_id = d.subject_id AND a.hadm_id = d.hadm_id
JOIN `physionet-data.mimiciv_3_1_hosp.d_icd_diagnoses` diag
  ON d.icd_code = diag.icd_code AND d.icd_version = diag.icd_version
GROUP BY d.icd_code, d.icd_version, diag.long_title
HAVING COUNT(DISTINCT a.hadm_id) >= 50
ORDER BY aki_patient_count DESC
LIMIT 20
