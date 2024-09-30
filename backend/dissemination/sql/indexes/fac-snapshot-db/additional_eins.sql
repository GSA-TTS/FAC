---------------------------------------
-- INDEXES on additional_eins
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_additional_eins_report_id_idx 
	on public_data_v1_0_0.additional_eins (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_additional_eins_report_id_fad
	on public_data_v1_0_0.additional_eins (report_id, fac_accepted_date);
