---------------------------------------
-- INDEXES on secondary_auditors
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_secondary_auditors_report_id_idx 
	on public_data_v1_0_0.secondary_auditors (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_secondary_auditors_report_id_fad
	on public_data_v1_0_0.secondary_auditors (report_id, fac_accepted_date);
