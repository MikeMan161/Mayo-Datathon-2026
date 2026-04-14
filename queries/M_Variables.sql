WITH base_cohort AS (
    -- Step 1: Filtered Admissions
    SELECT DISTINCT d.subject_id, d.hadm_id, a.admittime, a.dischtime
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd` d
    INNER JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a ON d.hadm_id = a.hadm_id
    WHERE (
        (d.icd_version = 10 AND d.icd_code IN ('C3400','C3401','C3402','C3410','C3411','C3412','C342','C3430','C3431','C3432','C3480','C3481','C3482','C3490','C3491','C3492', 'C7800','C7801','C7802','C4650','C4651','C4652','C7A090'))
        OR (d.icd_version = 9 AND d.icd_code IN ('1620','1622','1623','1624','1625','1628','1629','1970','1764'))
    )
    AND d.hadm_id NOT IN (
        SELECT hadm_id FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
        WHERE (seq_num = 1 AND ((icd_version = 9 AND icd_code IN ('584','5845','5846','5847','5848','5849')) OR (icd_version = 10 AND icd_code IN ('N17','N170','N171','N172','N178','N179'))))
        OR (icd_code IN ('V451','V4511','V4512'))
    )
),

all_heights AS (
    -- Unified Heights
    SELECT subject_id, SAFE_CAST(result_value AS FLOAT64) AS height
    FROM `physionet-data.mimiciv_3_1_hosp.omr` WHERE result_name = 'Height (Inches)'
    UNION ALL
    SELECT subject_id, valuenum * 0.393701 -- Convert cm to inches
    FROM `physionet-data.mimiciv_3_1_icu.chartevents` WHERE itemid = 226730
),

patient_height AS (
    SELECT subject_id, AVG(height) AS avg_height_in 
    FROM all_heights GROUP BY subject_id
),

all_weights AS (
    -- Unified Weights
    SELECT subject_id, chartdate AS weight_time, SAFE_CAST(result_value AS FLOAT64) AS weight_lb
    FROM `physionet-data.mimiciv_3_1_hosp.omr` WHERE result_name = 'Weight (Lbs)'
    UNION ALL
    SELECT subject_id, CAST(charttime AS DATE), valuenum * 2.20462 -- Convert kg to lbs
    FROM `physionet-data.mimiciv_3_1_icu.chartevents` WHERE itemid = 226512
),

closest_weight AS (
    -- Rank weight by proximity to admission
    SELECT 
        c.hadm_id,
        w.weight_lb,
        ROW_NUMBER() OVER(PARTITION BY c.hadm_id ORDER BY ABS(DATE_DIFF(w.weight_time, CAST(c.admittime AS DATE), DAY))) as rn
    FROM base_cohort c
    JOIN all_weights w ON c.subject_id = w.subject_id
),

closest_precalc_bmi AS (
    -- Rank precalculated BMI by proximity to admission
    SELECT 
        c.hadm_id,
        SAFE_CAST(pb.result_value AS FLOAT64) as bmi_val,
        ROW_NUMBER() OVER(PARTITION BY c.hadm_id ORDER BY ABS(DATE_DIFF(pb.chartdate, CAST(c.admittime AS DATE), DAY))) as rn
    FROM base_cohort c
    JOIN `physionet-data.mimiciv_3_1_hosp.omr` pb ON c.subject_id = pb.subject_id
    WHERE pb.result_name = 'BMI (kg/m2)'
)

SELECT
    bc.subject_id,
    bc.hadm_id,
    p.gender,
    (p.anchor_age + (EXTRACT(YEAR FROM a.admittime) - p.anchor_year)) AS age,
    a.race,
    a.hospital_expire_flag AS died_in_hospital,
    -- Final BMI Selection Logic (Hidden height/weight used here)
    COALESCE(
        cbmi.bmi_val,
        ROUND(703 * cw.weight_lb / (ph.avg_height_in * ph.avg_height_in), 2)
    ) AS final_bmi,
    CASE
        WHEN TIMESTAMP_DIFF(a.dischtime, a.admittime, HOUR) < 24  THEN 'Hospital Stay: <24 hours'
        WHEN TIMESTAMP_DIFF(a.dischtime, a.admittime, HOUR) < 48  THEN 'Hospital Stay: 24-48 hours'
        WHEN TIMESTAMP_DIFF(a.dischtime, a.admittime, HOUR) < 72  THEN 'Hospital Stay: 48-72 hours'
        WHEN TIMESTAMP_DIFF(a.dischtime, a.admittime, HOUR) < 96  THEN 'Hospital Stay: 72-96 hours'
        WHEN TIMESTAMP_DIFF(a.dischtime, a.admittime, HOUR) < 120 THEN 'Hospital Stay: 96-120 hours'
        WHEN TIMESTAMP_DIFF(a.dischtime, a.admittime, HOUR) < 144 THEN 'Hospital Stay: 120-144 hours'
        WHEN TIMESTAMP_DIFF(a.dischtime, a.admittime, HOUR) < 168 THEN 'Hospital Stay: 144-168 hours'
        ELSE 'Hospital Stay: >168 hours'
    END AS hospital_stay_bucket
FROM base_cohort bc
INNER JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a ON bc.hadm_id = a.hadm_id
INNER JOIN `physionet-data.mimiciv_3_1_hosp.patients` p ON bc.subject_id = p.subject_id
LEFT JOIN patient_height ph ON bc.subject_id = ph.subject_id
LEFT JOIN closest_weight cw ON bc.hadm_id = cw.hadm_id AND cw.rn = 1
LEFT JOIN closest_precalc_bmi cbmi ON bc.hadm_id = cbmi.hadm_id AND cbmi.rn = 1
WHERE TIMESTAMP_DIFF(a.dischtime, a.admittime, HOUR) >= 0
ORDER BY bc.subject_id, a.admittime;
