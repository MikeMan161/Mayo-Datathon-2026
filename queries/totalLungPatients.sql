SELECT DISTINCT
    d.subject_id,
    a.hadm_id,
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
FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd` d
INNER JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a ON d.hadm_id = a.hadm_id
WHERE (
    (d.icd_version = 10 AND d.icd_code IN (
        'C3400','C3401','C3402',
        'C3410','C3411','C3412',
        'C342',
        'C3430','C3431','C3432',
        'C3480','C3481','C3482',
        'C3490','C3491','C3492'
    ))
    OR (d.icd_version = 10 AND d.icd_code IN (
        'C7800','C7801','C7802',
        'C4650','C4651','C4652',
        'C7A090'
    ))
    OR (d.icd_version = 9 AND d.icd_code IN (
        '1620','1622','1623','1624','1625','1628','1629'
    ))
    OR (d.icd_version = 9 AND d.icd_code IN (
        '1970','1764'
    ))
)
AND d.hadm_id NOT IN (
    SELECT hadm_id FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE seq_num = 1
    AND (
        (icd_version = 9 AND icd_code IN ('584','5845','5846','5847','5848','5849'))
        OR (icd_version = 10 AND icd_code IN ('N17','N170','N171','N172','N178','N179'))
    )
)
AND d.hadm_id NOT IN (
    SELECT hadm_id FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE icd_code IN ('V451','V4511','V4512')
)
AND TIMESTAMP_DIFF(a.dischtime, a.admittime, HOUR) >= 0
