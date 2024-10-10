---------------------------------------
-- INDEXES on secondary_auditors
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_secondary_auditors_report_id_idx 
	on public_data_v1_0_0.secondary_auditors (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_secondary_auditors_report_id_fad_idx
	on public_data_v1_0_0.secondary_auditors (report_id, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_batch_secondary_auditors_idx
    ON public_data_v1_0_0.secondary_auditors (batch_number);
