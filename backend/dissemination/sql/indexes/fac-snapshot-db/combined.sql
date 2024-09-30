
---------------------------------------
-- INDEXES on combined
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_report_id_idx 
	on public_data_v1_0_0.combined (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_report_id_fad
	on public_data_v1_0_0.combined (report_id, fac_accepted_date);

-- Some of these may be redundant? Not sure how indexes overlap (or don't).
CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_fad_aln
	on public_data_v1_0_0.combined (fac_accepted_date, aln);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_fad_agency
	on public_data_v1_0_0.combined (fac_accepted_date, federal_agency_prefix);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_fad_agency_ext
	on public_data_v1_0_0.combined (fac_accepted_date, federal_agency_prefix, federal_award_extension);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_report_id_fad_aln
	on public_data_v1_0_0.combined (report_id, fac_accepted_date, aln);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_report_id_fad_agency_ext
	on public_data_v1_0_0.combined (report_id, federal_agency_prefix, federal_award_extension);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_auditee_certify_name_idx 
	ON public_data_v1_0_0.combined 
	((lower(auditee_certify_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_auditee_name_idx 
	ON public_data_v1_0_0.combined 
	((lower(auditee_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_auditor_certify_name_idx 
	ON public_data_v1_0_0.combined 
	((lower(auditor_certify_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_auditor_contact_name_idx 
	ON public_data_v1_0_0.combined 
	((lower(auditor_contact_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_auditor_firm_name_idx 
	ON public_data_v1_0_0.combined 
	((lower(auditor_firm_name)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_auditee_email_idx 
	on public_data_v1_0_0.combined ((lower(auditee_email)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_auditor_email_idx 
	on public_data_v1_0_0.combined ((lower(auditor_email)));

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_start_date_idx 
	ON public_data_v1_0_0.combined (fy_start_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_end_date_idx 
	ON public_data_v1_0_0.combined (fy_end_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_auditee_uei_idx 
	ON public_data_v1_0_0.combined (auditee_uei);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_auditee_ein_idx
	ON public_data_v1_0_0.combined (auditee_ein);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_federal_agency_prefix_idx 
	on public_data_v1_0_0.combined (federal_agency_prefix);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_federal_award_extension_idx 
	on public_data_v1_0_0.combined (federal_award_extension);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_audit_year_idx 
	on public_data_v1_0_0.combined (audit_year);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_combined_aln_idx 
	on public_data_v1_0_0.combined (aln);
