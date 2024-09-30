---------------------------------------
-- INDEXES on passthrough
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_passthrough_report_id_idx 
	on public_data_v1_0_0.passthrough (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_passthrough_report_id_fad
	on public_data_v1_0_0.passthrough (report_id, fac_accepted_date);
