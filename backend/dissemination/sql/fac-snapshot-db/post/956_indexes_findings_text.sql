---------------------------------------
-- INDEXES on findings_text
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_findings_text_report_id_idx 
	on public_data_v1_0_0.findings_text (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_findings_text_report_id_fad
	on public_data_v1_0_0.findings_text (report_id, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_batch_findings_text_idx
    ON public_data_v1_0_0.findings_text (batch_number);
