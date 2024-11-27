---------------------------------------
-- INDEXES on notes_to_sefa
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_notes_to_sefa_report_id_idx 
	on public_data_v1_0_0.notes_to_sefa (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_notes_to_sefa_report_id_fad
	on public_data_v1_0_0.notes_to_sefa (report_id, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_batch_notes_to_sefa_idx
    ON public_data_v1_0_0.notes_to_sefa (batch_number);
