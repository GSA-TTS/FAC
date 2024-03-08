CREATE SEQUENCE dissemination_combined_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE;

-----------------------
-- dissemination_combined
-- This table is used primarily by search.
CREATE MATERIALIZED VIEW IF NOT EXISTS 
	dissemination_combined AS 
	SELECT 
		nextval('dissemination_combined_id_seq') AS id,
		dg.report_id,
		dfa.award_reference,
		df.reference_number,
		dg.fac_accepted_date::date,
		
		dfa.federal_agency_prefix,
		dfa.federal_award_extension,
		dfa.federal_agency_prefix||'.'||dfa.federal_award_extension as aln,
		dfa.additional_award_identification,

		dg.cognizant_agency,
		dg.oversight_agency,
		dg.auditee_uei,
		dg.auditee_ein,
		dg.audit_type,
		dg.audit_year,
		dg.auditee_certify_name,
		dg.auditee_contact_name,
		dg.auditee_email,
		dg.auditee_name,
		dg.auditee_city,
		dg.auditee_state,
		dg.auditee_zip,
		dg.auditor_state,
		dg.auditor_city,
		dg.auditor_zip,
		dg.auditor_contact_name,
		dg.auditor_email,
		dg.auditor_firm_name,
		dg.auditor_ein,

		dfa.amount_expended,
		dfa.findings_count,
		dfa.is_direct::boolean,
		dfa.is_loan::boolean,
		dfa.is_major::boolean,
		dfa.is_passthrough_award::boolean,
		dfa.audit_report_type,
		dfa.passthrough_amount,
		dfa.federal_program_name,
		dfa.federal_program_total,
		dfa.cluster_name,
		dfa.other_cluster_name,
		dfa.state_cluster_name,
		dfa.cluster_total,

		df.is_material_weakness::boolean,
		df.is_modified_opinion::boolean,
		df.is_other_findings::boolean,
		df.is_other_matters::boolean,
		df.is_questioned_costs::boolean,
		df.is_repeat_finding::boolean,
		df.is_significant_deficiency::boolean,
		df.prior_finding_ref_numbers,
		df.type_requirement, 
		dg.is_public
	from
		dissemination_federalaward dfa,
		dissemination_finding df,
		dissemination_general dg 
	where 
		df.award_reference = dfa.award_reference
		and dg.report_id = dfa.report_id 
		and dg.report_id = df.report_id
		;
