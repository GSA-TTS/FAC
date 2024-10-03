---------------------------------------
-- INDEXES on federal_awards
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_id_idx 
	on public_data_v1_0_0.federal_awards (id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_report_id_idx 
	on public_data_v1_0_0.federal_awards (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_report_id_fad
	on public_data_v1_0_0.federal_awards (report_id, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_rid_fap
    ON public_data_v1_0_0.federal_awards (report_id, federal_agency_prefix);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_rid_fap_fext
    ON public_data_v1_0_0.federal_awards (report_id, federal_agency_prefix, federal_award_extension);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_rid_fap_fext_fad
    ON public_data_v1_0_0.federal_awards (report_id, federal_agency_prefix, federal_award_extension, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_fap_fext_cnt
    ON public_data_v1_0_0.federal_awards (federal_agency_prefix,federal_award_extension,findings_count);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_rid_aln
    ON public_data_v1_0_0.federal_awards (report_id, aln);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_rid_aln_fad
    ON public_data_v1_0_0.federal_awards (report_id, aln, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_awards_aln_cnt
    ON public_data_v1_0_0.federal_awards (aln,findings_count);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_batch_fa 
    ON public_data_v1_0_0.federal_awards (batch_number);
