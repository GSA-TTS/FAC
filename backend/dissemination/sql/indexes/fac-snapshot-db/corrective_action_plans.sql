---------------------------------------
-- INDEXES on corrective_action_plans
---------------------------------------
CREATE INDEX IF NOT EXISTS fac_snapshot_db_corrective_action_plans_report_id_idx 
	on public_data_v1_0_0.corrective_action_plans (report_id);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_corrective_action_plans_report_id_fad_idx
	on public_data_v1_0_0.corrective_action_plans (report_id, fac_accepted_date);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_corrective_action_plans_report_id_fad_frn_idx
	on public_data_v1_0_0.corrective_action_plans (report_id, fac_accepted_date, finding_ref_number);

CREATE INDEX IF NOT EXISTS fac_snapshot_db_federal_batch_corrective_action_plans_idx
    ON public_data_v1_0_0.corrective_action_plans (batch_number);
