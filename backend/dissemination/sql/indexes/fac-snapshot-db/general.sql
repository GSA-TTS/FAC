
---------------------------------------
-- INDEXES on general
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_report_id_idx 
	on public_data_v1_0_0.general (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_report_id_fad
	on public_data_v1_0_0.general (report_id, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_report_id_fad
	on public_data_v1_0_0.general (report_id, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_auditee_certify_name_idx 
	ON public_data_v1_0_0.general 
	((lower(auditee_certify_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_auditee_name_idx 
	ON public_data_v1_0_0.general 
	((lower(auditee_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_auditor_certify_name_idx 
	ON public_data_v1_0_0.general 
	((lower(auditor_certify_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_auditor_contact_name_idx 
	ON public_data_v1_0_0.general 
	((lower(auditor_contact_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_auditor_firm_name_idx 
	ON public_data_v1_0_0.general 
	((lower(auditor_firm_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_auditee_email_idx 
	on public_data_v1_0_0.general ((lower(auditee_email)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_auditor_email_idx 
	on public_data_v1_0_0.general ((lower(auditor_email)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_start_date_idx 
	ON public_data_v1_0_0.general (fy_start_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_end_date_idx 
	ON public_data_v1_0_0.general (fy_end_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_auditee_uei_idx 
	ON public_data_v1_0_0.general (auditee_uei);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_auditee_ein_idx
	ON public_data_v1_0_0.general (auditee_ein);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_general_audit_year_idx 
	on public_data_v1_0_0.general (audit_year);
