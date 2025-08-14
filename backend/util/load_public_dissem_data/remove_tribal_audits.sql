-- This removes ALL tribal audits from a 
-- local data instance. You should never run this in production.
-- This was removed from the `prepare_dump` script because it is 
-- too large and complex to embed directly.
WITH 
  report_ids_to_delete AS (
    -- Select all the reports where they explicitly said not to disseminate.
    SELECT report_id
      FROM audit_singleauditchecklist
      WHERE
        tribal_data_consent->>'is_tribal_information_authorized_to_be_public' = 'false'
    UNION
    -- Union this with all the reports that are tribal and no attestation has 
    -- yet been made. These would be in-progress to some degree or another.
    SELECT report_id
      FROM audit_singleauditchecklist
      WHERE
        general_information->>'user_provided_organization_type' = 'tribal'
      AND
        tribal_data_consent->>'is_tribal_information_authorized_to_be_public' IS NULL
  ),
  sac_ids_to_delete AS (
    SELECT id
      FROM audit_singleauditchecklist
      WHERE tribal_data_consent->>'is_tribal_information_authorized_to_be_public' = 'false'
    UNION
    SELECT id
      FROM audit_singleauditchecklist
      WHERE
        general_information->>'user_provided_organization_type' = 'tribal'
      AND
        tribal_data_consent->>'is_tribal_information_authorized_to_be_public' IS NULL
  ),
  captext_deleted AS (
    DELETE FROM 
      dissemination_captext
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  findingtext_deleted AS (
    DELETE FROM 
      dissemination_findingtext
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  migrationinspectionrecord_deleted AS (
    DELETE FROM 
      dissemination_migrationinspectionrecord
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  note_deleted AS (
    DELETE FROM 
      dissemination_note
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  -- Now, the tables dependent on 'audit' and 'singleauditchecklist'
  access_deleted AS (
    DELETE FROM audit_access WHERE sac_id IN (SELECT * FROM sac_ids_to_delete) 
  ),
  deletedaccess_deleted AS (
    DELETE FROM audit_deletedaccess WHERE sac_id IN (SELECT * FROM sac_ids_to_delete)
  ),
  deleted_excelfile AS (
    DELETE FROM audit_excelfile WHERE sac_id IN (SELECT * FROM sac_ids_to_delete)
  ),
  deleted_validationwaiver AS (
    DELETE FROM audit_sacvalidationwaiver WHERE report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  -- Delete this entire table.
  deleted_checklistflow AS (
    DELETE FROM audit_singleauditchecklistflow WHERE 1=1
  ),
  deleted_singleauditreportfile AS (
    DELETE FROM audit_singleauditreportfile WHERE sac_id IN (SELECT * FROM sac_ids_to_delete)
  ),
  deleted_subevent AS (
    DELETE FROM audit_submissionevent WHERE sac_id IN (SELECT * FROM sac_ids_to_delete)
  ),
  -- Now the audit and SAC
  audit_deleted AS (
    DELETE FROM
      audit_audit
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  sac_deleted AS (
    DELETE FROM
      audit_singleauditchecklist
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  invalid_deleted as (
	  DELETE FROM 
	      dissemination_invalidauditrecord
	    WHERE
	      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  awards_deleted AS (
    DELETE FROM
      dissemination_federalaward
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  findings_deleted AS (
    DELETE FROM
      dissemination_finding
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  passthrough_deleted AS (
    DELETE FROM
      dissemination_passthrough
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  ein_deleted AS (
    DELETE FROM
      dissemination_additionalein
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  uei_deleted AS (
    DELETE FROM
      dissemination_additionaluei
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  ),
  secaudit_deleted AS (
    DELETE FROM
      dissemination_secondaryauditor
    WHERE
      report_id IN (SELECT * FROM report_ids_to_delete)
  )
DELETE FROM dissemination_general
WHERE report_id IN (SELECT * from report_ids_to_delete);
