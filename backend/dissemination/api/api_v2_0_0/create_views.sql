begin;

---------------------------------------
-- finding_text
---------------------------------------
create view api_v2_0_0.findings_text as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ft.finding_ref_number,
        ft.contains_chart_or_table,
        ft.finding_text
    from
        dissemination_findingtext ft,
        dissemination_general gen
    where
        ft.report_id = gen.report_id
         and
        (gen.is_public = true
        or (gen.is_public = false and api_v2_0_0_functions.has_tribal_data_access()))
    order by ft.id
;

---------------------------------------
-- additional_ueis
---------------------------------------
create view api_v2_0_0.additional_ueis as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        uei.additional_uei
    from
        dissemination_general gen,
        dissemination_additionaluei uei
    where
        gen.report_id = uei.report_id
    order by uei.id
;

---------------------------------------
-- finding
---------------------------------------
create view api_v2_0_0.findings as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        finding.award_reference,
        finding.reference_number,
        finding.is_material_weakness,
        finding.is_modified_opinion,
        finding.is_other_findings,
        finding.is_other_matters,
        finding.prior_finding_ref_numbers,
        finding.is_questioned_costs,
        finding.is_repeat_finding,
        finding.is_significant_deficiency,
        finding.type_requirement
    from
        dissemination_finding finding,
        dissemination_general gen
    where
        finding.report_id = gen.report_id
    order by finding.id
;

---------------------------------------
-- federal award
---------------------------------------
create view api_v2_0_0.federal_awards as
    select
        award.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        award.award_reference,
        award.federal_agency_prefix,
        award.federal_award_extension,
        award.additional_award_identification,
        award.federal_program_name,
        award.amount_expended,
        award.cluster_name,
        award.other_cluster_name,
        award.state_cluster_name,
        award.cluster_total,
        award.federal_program_total,
        award.is_major,
        award.is_loan,
        award.loan_balance,
        award.is_direct,
        award.audit_report_type,
        award.findings_count,
        award.is_passthrough_award,
        award.passthrough_amount
    from
        dissemination_federalaward award,
        dissemination_general gen
    where
        award.report_id = gen.report_id
    order by award.id
;


---------------------------------------
-- corrective_action_plan
---------------------------------------
create view api_v2_0_0.corrective_action_plans as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        ct.finding_ref_number,
        ct.contains_chart_or_table,
        ct.planned_action
    from
        dissemination_CAPText ct,
        dissemination_General gen
    where
        ct.report_id = gen.report_id
        and
        (gen.is_public = true
        or (gen.is_public = false and api_v2_0_0_functions.has_tribal_data_access()))
    order by ct.id
;

---------------------------------------
-- notes_to_sefa
---------------------------------------
create view api_v2_0_0.notes_to_sefa as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        note.note_title as title,
        note.accounting_policies,
        note.is_minimis_rate_used,
        note.rate_explained,
        note.content,
        note.contains_chart_or_table
    from
        dissemination_general gen,
        dissemination_note note
    where
        note.report_id = gen.report_id
        and
        (gen.is_public = true
        or (gen.is_public = false and api_v2_0_0_functions.has_tribal_data_access()))
    order by note.id
;

---------------------------------------
-- passthrough
---------------------------------------
create view api_v2_0_0.passthrough as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        pass.award_reference,
        pass.passthrough_id,
        pass.passthrough_name
    from
        dissemination_general as gen,
        dissemination_passthrough as pass
    where
        gen.report_id = pass.report_id
    order by pass.id
;


---------------------------------------
-- general
---------------------------------------
create view api_v2_0_0.general as
    select
        -- every table starts with report_id, UEI, and year
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        gen.auditee_certify_name,
        gen.auditee_certify_title,
        gen.auditee_contact_name,
        gen.auditee_email,
        gen.auditee_name,
        gen.auditee_phone,
        gen.auditee_contact_title,
        gen.auditee_address_line_1,
        gen.auditee_city,
        gen.auditee_state,
        gen.auditee_ein,
        gen.auditee_zip,
        -- auditor
        gen.auditor_certify_name,
        gen.auditor_certify_title,
        gen.auditor_phone,
        gen.auditor_state,
        gen.auditor_city,
        gen.auditor_contact_title,
        gen.auditor_address_line_1,
        gen.auditor_zip,
        gen.auditor_country,
        gen.auditor_contact_name,
        gen.auditor_email,
        gen.auditor_firm_name,
        gen.auditor_foreign_address,
        gen.auditor_ein,
        -- agency
        gen.cognizant_agency,
        gen.oversight_agency,
        -- dates
        gen.date_created,
        gen.ready_for_certification_date,
        gen.auditor_certified_date,
        gen.auditee_certified_date,
        gen.submitted_date,
        gen.fac_accepted_date,
        gen.fy_end_date,
        gen.fy_start_date,
        gen.audit_type,
        gen.gaap_results,
        gen.sp_framework_basis,
        gen.is_sp_framework_required,
        gen.sp_framework_opinions,
        gen.is_going_concern_included,
        gen.is_internal_control_deficiency_disclosed,
        gen.is_internal_control_material_weakness_disclosed,
        gen.is_material_noncompliance_disclosed,
        gen.dollar_threshold,
        gen.is_low_risk_auditee,
        gen.agencies_with_prior_findings,
        gen.entity_type,
        gen.number_months,
        gen.audit_period_covered,
        gen.total_amount_expended,
        gen.type_audit_code,
        gen.is_public,
        gen.data_source,
        gen.is_aicpa_audit_guide_included,
        gen.is_additional_ueis,
        CASE EXISTS(SELECT ein.report_id FROM dissemination_additionalein ein WHERE ein.report_id = gen.report_id)
            WHEN FALSE THEN 'No'
            ELSE 'Yes'
        END AS is_multiple_eins,
        CASE EXISTS(SELECT aud.report_id FROM dissemination_secondaryauditor aud WHERE aud.report_id = gen.report_id)
            WHEN FALSE THEN 'No'
            ELSE 'Yes'
        END AS is_secondary_auditors
    from
        dissemination_general gen
    order by gen.id
;

---------------------------------------
-- auditor (secondary auditor)
---------------------------------------
create view api_v2_0_0.secondary_auditors as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        sa.auditor_ein,
        sa.auditor_name,
        sa.contact_name,
        sa.contact_title,
        sa.contact_email,
        sa.contact_phone,
        sa.address_street,
        sa.address_city,
        sa.address_state,
        sa.address_zipcode
    from
        dissemination_General gen,
        dissemination_SecondaryAuditor sa
    where
        sa.report_id = gen.report_id
    order by sa.id
;

create view api_v2_0_0.additional_eins as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        ein.additional_ein
    from
        dissemination_general gen,
        dissemination_additionalein ein
    where
        gen.report_id = ein.report_id
    order by ein.id
;

commit;

notify pgrst,
       'reload schema';


---------------------------------------
-- materialized view - generalxawardsxfindings
---------------------------------------
create view api_v2_0_0.generalxawardsxfindings as
    select
        dc.id,
        dg.report_id,
		dc.award_reference,
		dc.reference_number,
		dc.aln,
		dc.agencies_with_prior_findings,
		dc.audit_period_covered,
		dc.audit_type,
		dc.audit_year,
		dc.auditee_address_line_1,
		dc.auditee_certified_date,
		dc.auditee_certify_name,
		dc.auditee_certify_title,
		dc.auditee_city,
		dc.auditee_contact_name,
		dc.auditee_contact_title,
		dc.auditee_ein,
		dc.auditee_email,
		dc.auditee_name,
		dc.auditee_phone,
		dc.auditee_state,
		dc.auditee_uei,
		dc.auditee_zip,
		dc.auditor_address_line_1,
		dc.auditor_certified_date,
		dc.auditor_certify_name,
		dc.auditor_certify_title,
		dc.auditor_city,
		dc.auditor_contact_name,
		dc.auditor_contact_title,
		dc.auditor_country,
		dc.auditor_ein,
		dc.auditor_email,
		dc.auditor_firm_name,
		dc.auditor_foreign_address,
		dc.auditor_phone,
		dc.auditor_state,
		dc.auditor_zip,
		dc.cognizant_agency,
		dc.data_source,
		dc.date_created,
		dc.dollar_threshold,
		dc.entity_type,
		dc.fac_accepted_date,
		dc.fy_end_date,
		dc.fy_start_date,
		dc.gaap_results,
		dc.is_additional_ueis,
		dc.is_aicpa_audit_guide_included,
		dc.is_going_concern_included,
		dc.is_internal_control_deficiency_disclosed,
		dc.is_internal_control_material_weakness_disclosed,
		dc.is_low_risk_auditee,
		dc.is_material_noncompliance_disclosed,
		dc.is_public,
		dc.is_sp_framework_required,
		dc.number_months,
		dc.oversight_agency,
		dc.ready_for_certification_date,
		dc.sp_framework_basis,
		dc.sp_framework_opinions,
		dc.submitted_date,
		dc.total_amount_expended,
		dc.type_audit_code,
		-- All of diss_federalaward
		dc.additional_award_identification,
		dc.amount_expended,
		dc.cluster_name,
		dc.cluster_total,
		dc.federal_agency_prefix,
		dc.federal_award_extension,
		dc.federal_program_name,
		dc.federal_program_total,
		dc.findings_count,
		dc.is_direct,
		dc.is_loan,
		dc.is_major,
		dc.is_passthrough_award,
		dc.loan_balance,
		dc.audit_report_type,
		dc.other_cluster_name,
		dc.passthrough_amount,
		dc.state_cluster_name,
		-- All of diss_finding
		dc.is_material_weakness,
		dc.is_modified_opinion,
		dc.is_other_findings,
		dc.is_other_matters,
		dc.is_questioned_costs,
		dc.is_repeat_finding,
		dc.is_significant_deficiency,
		dc.prior_finding_ref_numbers,
		dc.type_requirement,
		-- ALL of Passthrough
		dc.passthrough_name,
		dc.passthrough_id
    from
        dissemination_combined AS dc
    order by dc.id
;
