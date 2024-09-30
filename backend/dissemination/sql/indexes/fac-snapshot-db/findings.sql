---------------------------------------
-- INDEXES on findings
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_findings_report_id_idx 
	on public_data_v1_0_0.findings (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_findings_report_id_fad
	on public_data_v1_0_0.findings (report_id, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_findings_rid_aref
	on public_data_v1_0_0.findings (report_id, award_reference);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_findings_rid_aref_fad
	on public_data_v1_0_0.findings (report_id, award_reference, fac_accepted_date);


