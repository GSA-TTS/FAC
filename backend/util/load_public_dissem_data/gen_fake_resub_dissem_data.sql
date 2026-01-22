-- Create coherent resubmission chains using ONLY:
--   auditee_uei + audit_year

WITH chains AS (
    SELECT
        auditee_uei,
        audit_year
    FROM dissemination_general
    WHERE auditee_uei IS NOT NULL
    GROUP BY auditee_uei, audit_year
    HAVING COUNT(*) >= 2
    LIMIT 200
),

ranked AS (
    SELECT
        g.report_id,
        ROW_NUMBER() OVER (
            PARTITION BY g.auditee_uei, g.audit_year
            ORDER BY g.fac_accepted_date NULLS LAST, g.report_id
        ) AS version,
        COUNT(*) OVER (
            PARTITION BY g.auditee_uei, g.audit_year
        ) AS max_version
    FROM dissemination_general g
    JOIN chains c
      ON g.auditee_uei = c.auditee_uei
     AND g.audit_year = c.audit_year
)

UPDATE dissemination_general g
SET
    resubmission_version = r.version,
    resubmission_status = CASE
        WHEN r.version = r.max_version
            THEN 'most_recent'
        ELSE 'deprecated_via_resubmission'
    END
FROM ranked r
WHERE g.report_id = r.report_id;
