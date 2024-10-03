---------------------------------------
-- INDEXES on additional_ueis
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_additional_ueis_report_id_idx 
	on public_data_v1_0_0.additional_ueis (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_additional_ueis_report_id_fad
	on public_data_v1_0_0.additional_ueis (report_id, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_batch_additional_ueis 
    ON public_data_v1_0_0.additional_ueis (batch_number);
