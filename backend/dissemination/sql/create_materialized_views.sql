CREATE SEQUENCE IF NOT EXISTS dissemination_combined_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE;

-----------------------
-- dissemination_combined
-- This table is used primarily by search.
CREATE MATERIALIZED VIEW IF NOT EXISTS 
	dissemination_combined_temp AS 
	SELECT
		nextval('dissemination_combined_id_seq') AS id,
		dg.report_id,
		dfa.award_reference,
		df.reference_number,
		-- Build a composite ALN in case we want/need it
		concat(dfa.federal_agency_prefix,'.',dfa.federal_award_extension) as aln,
		-- All of diss_general as of 20240313
		dg.agencies_with_prior_findings,
		dg.audit_period_covered,
		dg.audit_type,
		dg.audit_year,
		dg.auditee_address_line_1,
		dg.auditee_certified_date,
		dg.auditee_certify_name,
		dg.auditee_certify_title,
		dg.auditee_city,
		dg.auditee_contact_name,
		dg.auditee_contact_title,
		dg.auditee_ein,
		dg.auditee_email,
		dg.auditee_name,
		dg.auditee_phone,
		dg.auditee_state,
		dg.auditee_uei,
		dg.auditee_zip,
		dg.auditor_address_line_1,
		dg.auditor_certified_date,
		dg.auditor_certify_name,
		dg.auditor_certify_title,
		dg.auditor_city,
		dg.auditor_contact_name,
		dg.auditor_contact_title,
		dg.auditor_country,
		dg.auditor_ein,
		dg.auditor_email,
		dg.auditor_firm_name,
		dg.auditor_foreign_address,
		dg.auditor_phone,
		dg.auditor_state,
		dg.auditor_zip,
		dg.cognizant_agency,
		dg.data_source,
		dg.date_created,
		dg.dollar_threshold,
		dg.entity_type,
		dg.fac_accepted_date,
		dg.fy_end_date,
		dg.fy_start_date,
		dg.gaap_results,
		dg.is_additional_ueis,
		dg.is_aicpa_audit_guide_included,
		dg.is_going_concern_included,
		dg.is_internal_control_deficiency_disclosed,
		dg.is_internal_control_material_weakness_disclosed,
		dg.is_low_risk_auditee,
		dg.is_material_noncompliance_disclosed,
		dg.is_public,
		dg.is_sp_framework_required,
		dg.number_months,
		dg.oversight_agency,
		dg.ready_for_certification_date,
		dg.sp_framework_basis,
		dg.sp_framework_opinions,
		dg.submitted_date,
		dg.total_amount_expended,
		dg.type_audit_code,
		-- All of diss_federalaward
		dfa.additional_award_identification,
		dfa.amount_expended,
		dfa.cluster_name,
		dfa.cluster_total,
		dfa.federal_agency_prefix,
		dfa.federal_award_extension,
		dfa.federal_program_name,
		dfa.federal_program_total,
		dfa.findings_count,
		dfa.is_direct,
		dfa.is_loan,
		dfa.is_major,
		dfa.is_passthrough_award,
		dfa.loan_balance,
		dfa.audit_report_type,
		dfa.other_cluster_name,
		dfa.passthrough_amount,
		dfa.state_cluster_name,
		-- All of diss_finding
		df.is_material_weakness,
		df.is_modified_opinion,
		df.is_other_findings,
		df.is_other_matters,
		df.is_questioned_costs,
		df.is_repeat_finding,
		df.is_significant_deficiency,
		df.prior_finding_ref_numbers,
		df.type_requirement,
		-- ALL of Passthrough
		dp.passthrough_name,
		dp.passthrough_id
	FROM 
		dissemination_federalaward dfa
	LEFT JOIN dissemination_general dg 
		ON dfa.report_id = dg.report_id
	LEFT JOIN dissemination_finding df 
		ON dfa.report_id = df.report_id 
		AND dfa.award_reference = df.award_reference
	LEFT JOIN dissemination_passthrough dp
		ON dfa.report_id = dp.report_id 
		AND dfa.award_reference = dp.award_reference
	;	


DROP MATERIALIZED VIEW IF EXISTS dissemination_combined;
ALTER SEQUENCE dissemination_combined_id_seq RESTART;
ALTER MATERIALIZED VIEW dissemination_combined_temp RENAME TO dissemination_combined;

CREATE INDEX IF NOT EXISTS dc_report_id_idx 
	on dissemination_combined (report_id);

CREATE INDEX IF NOT EXISTS dc_auditee_certify_name_idx 
	ON dissemination_combined 
	((lower(auditee_certify_name)));

CREATE INDEX IF NOT EXISTS dc_auditee_name_idx 
	ON dissemination_combined 
	((lower(auditee_name)));

CREATE INDEX IF NOT EXISTS dc_auditor_certify_name_idx 
	ON dissemination_combined 
	((lower(auditor_certify_name)));

CREATE INDEX IF NOT EXISTS dc_auditor_contact_name_idx 
	ON dissemination_combined 
	((lower(auditor_contact_name)));

CREATE INDEX IF NOT EXISTS dc_auditor_firm_name_idx 
	ON dissemination_combined 
	((lower(auditor_firm_name)));

CREATE INDEX IF NOT EXISTS dc_auditee_email_idx 
	on dissemination_combined ((lower(auditee_email)));

CREATE INDEX IF NOT EXISTS dc_auditor_email_idx 
	on dissemination_combined ((lower(auditor_email)));

CREATE INDEX IF NOT EXISTS dc_start_date_idx 
	ON dissemination_combined (fy_start_date);

CREATE INDEX IF NOT EXISTS dc_end_date_idx 
	ON dissemination_combined (fy_end_date);

CREATE INDEX IF NOT EXISTS dc_auditee_uei_idx 
	ON dissemination_combined (auditee_uei);

CREATE INDEX IF NOT EXISTS dc_auditee_ein_idx
	ON dissemination_combined (auditee_ein);

CREATE INDEX IF NOT EXISTS dc_federal_agency_prefix_idx 
	on dissemination_combined (federal_agency_prefix);

CREATE INDEX IF NOT EXISTS dc_federal_award_extension_idx 
	on dissemination_combined (federal_award_extension);

CREATE INDEX IF NOT EXISTS dc_audit_year_idx 
	on dissemination_combined (audit_year);

CREATE INDEX IF NOT EXISTS dc_aln_idx 
	on dissemination_combined (aln);
