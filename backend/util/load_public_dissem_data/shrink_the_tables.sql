
WITH keepers AS (
    (SELECT id as sac_id, report_id
      FROM audit_singleauditchecklist
      where
      	general_information->>'auditee_fiscal_period_end' like '2016%'
        or
        general_information->>'auditee_fiscal_period_end' like '2017%'
        or
        general_information->>'auditee_fiscal_period_end' like '2018%'
        or
        general_information->>'auditee_fiscal_period_end' like '2019%'
        or
        general_information->>'auditee_fiscal_period_end' like '2020%'
        or
        general_information->>'auditee_fiscal_period_end' like '2021%'
        or
        general_information->>'auditee_fiscal_period_end' like '2022%'
        or
        general_information->>'auditee_fiscal_period_end' like '2023%'
      	order by id asc limit 20000)
  ),
  captext_deleted AS (
    DELETE FROM 
      dissemination_captext
    WHERE
      report_id not IN (SELECT report_id FROM keepers)
  ),
  findingtext_deleted AS (
    DELETE FROM 
      dissemination_findingtext
    WHERE
      report_id not IN (SELECT report_id FROM keepers)
  ),
  migrationinspectionrecord_deleted AS (
    DELETE FROM 
      dissemination_migrationinspectionrecord
    WHERE
      report_id not IN (SELECT report_id FROM keepers)
  ),
  note_deleted AS (
    DELETE FROM 
      dissemination_note
    WHERE
      report_id not IN (SELECT report_id FROM keepers)
  ),
  -- Now, the tables dependent on 'audit' and 'singleauditchecklist'
  access_deleted AS (
    DELETE FROM audit_access WHERE sac_id NOT IN (SELECT sac_id FROM keepers) 
  ),
  deletedaccess_deleted AS (
    DELETE FROM audit_deletedaccess WHERE sac_id NOT IN (SELECT sac_id FROM keepers)
  ),
  deleted_excelfile AS (
    DELETE FROM audit_excelfile WHERE sac_id NOT IN (SELECT sac_id FROM keepers)
  ),
  deleted_validationwaiver AS (
    DELETE FROM audit_sacvalidationwaiver WHERE report_id NOT IN (SELECT report_id FROM keepers)
  ),
  -- Get rid of this whole table
  deleted_auditvalwaiver as (
  	delete from audit_auditvalidationwaiver where 1=1
  ),
  -- Delete this entire table.
  deleted_checklistflow AS (
    DELETE FROM audit_singleauditchecklistflow WHERE 1=1
  ),
  deleted_singleauditreportfile AS (
    DELETE FROM audit_singleauditreportfile WHERE sac_id NOT IN (SELECT sac_id FROM keepers)
  ),
  deleted_subevent AS (
    DELETE FROM audit_submissionevent WHERE sac_id NOT IN (SELECT sac_id FROM keepers)
  ),
  -- Now the audit and SAC
  audit_deleted AS (
    DELETE FROM
      audit_audit
    WHERE
      report_id NOT IN (SELECT report_id FROM keepers)
  ),
  sac_deleted AS (
    DELETE FROM
      audit_singleauditchecklist
    WHERE
      report_id NOT IN (SELECT report_id FROM keepers)
  ),
  history_deleted AS (
    DELETE FROM
      audit_history
    WHERE
      report_id NOT IN (SELECT report_id FROM keepers)
  ),
  invalid_deleted as (
	  DELETE FROM 
	      dissemination_invalidauditrecord
	    WHERE
	      report_id NOT IN (SELECT report_id FROM keepers)
  ),
  awards_deleted AS (
    DELETE FROM
      dissemination_federalaward
    WHERE
      report_id NOT IN (SELECT report_id FROM keepers)
  ),
  findings_deleted AS (
    DELETE FROM
      dissemination_finding
    WHERE
      report_id NOT IN (SELECT report_id FROM keepers)
  ),
  passthrough_deleted AS (
    DELETE FROM
      dissemination_passthrough
    WHERE
      report_id NOT IN (SELECT report_id FROM keepers)
  ),
  ein_deleted AS (
    DELETE FROM
      dissemination_additionalein
    WHERE
      report_id NOT IN (SELECT report_id FROM keepers)
  ),
  uei_deleted AS (
    DELETE FROM
      dissemination_additionaluei
    WHERE
      report_id NOT IN (SELECT report_id FROM keepers)
  ),
  secaudit_deleted AS (
    DELETE FROM
      dissemination_secondaryauditor
    WHERE
      report_id NOT IN (SELECT report_id FROM keepers)
  )
DELETE FROM dissemination_general
WHERE report_id NOT IN (SELECT report_id from keepers);
