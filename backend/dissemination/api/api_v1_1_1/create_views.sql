begin;

---------------------------------------
-- finding_text
---------------------------------------
create view api_v1_1_1.findings_text as
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
        api_v1_1_0_functions.is_public_audit_or_authorized_user(gen.is_public)
    order by ft.id
;

---------------------------------------
-- additional_ueis
---------------------------------------
create view api_v1_1_1.additional_ueis as
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
create view api_v1_1_1.findings as
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
create view api_v1_1_1.federal_awards as
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
create view api_v1_1_1.corrective_action_plans as
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
        api_v1_1_0_functions.is_public_audit_or_authorized_user(gen.is_public)
    order by ct.id
;

---------------------------------------
-- notes_to_sefa
---------------------------------------
create view api_v1_1_1.notes_to_sefa as
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
        api_v1_1_0_functions.is_public_audit_or_authorized_user(gen.is_public)
    order by note.id
;

---------------------------------------
-- passthrough
---------------------------------------
create view api_v1_1_1.passthrough as
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
create view api_v1_1_1.general as
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
        --- audit info and metadata
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
        gen.resubmission_version,
        gen.resubmission_status,
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
create view api_v1_1_1.secondary_auditors as
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

---------------------------------------
-- additional eins
---------------------------------------
create view api_v1_1_1.additional_eins as
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

---------------------------------------
-- resubmission metadata
---------------------------------------
create view api_v1_1_1.resubmission as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        resub.version,
        resub.status,
        resub.previous_report_id,
        resub.next_report_id
    from
        dissemination_general gen,
        dissemination_resubmission resub
    where
        gen.report_id = resub.report_id
    order by resub.id
;

-- Specify every field in dissemination_combined, omitting the id.
-- Generated fields like ALN are done in the creation of the table, not here.
create view api_v1_1_1.combined as
    select
        combined.report_id,
        combined.award_reference,
        combined.reference_number,
        combined.aln,
        combined.agencies_with_prior_findings,
        combined.audit_period_covered,
        combined.audit_type,
        combined.audit_year,
        combined.auditee_address_line_1,
        combined.auditee_certified_date,
        combined.auditee_certify_name,
        combined.auditee_certify_title,
        combined.auditee_city,
        combined.auditee_contact_name,
        combined.auditee_contact_title,
        combined.auditee_ein,
        combined.auditee_email,
        combined.auditee_name,
        combined.auditee_phone,
        combined.auditee_state,
        combined.auditee_uei,
        combined.auditee_zip,
        combined.auditor_address_line_1,
        combined.auditor_certified_date,
        combined.auditor_certify_name,
        combined.auditor_certify_title,
        combined.auditor_city,
        combined.auditor_contact_name,
        combined.auditor_contact_title,
        combined.auditor_country,
        combined.auditor_ein,
        combined.auditor_email,
        combined.auditor_firm_name,
        combined.auditor_foreign_address,
        combined.auditor_phone,
        combined.auditor_state,
        combined.auditor_zip,
        combined.resubmission_version,
        combined.resubmission_status,
        combined.cognizant_agency,
        combined.data_source,
        combined.date_created,
        combined.dollar_threshold,
        combined.entity_type,
        combined.fac_accepted_date,
        combined.fy_end_date,
        combined.fy_start_date,
        combined.gaap_results,
        combined.is_additional_ueis,
        combined.is_aicpa_audit_guide_included,
        combined.is_going_concern_included,
        combined.is_internal_control_deficiency_disclosed,
        combined.is_internal_control_material_weakness_disclosed,
        combined.is_low_risk_auditee,
        combined.is_material_noncompliance_disclosed,
        combined.is_public,
        combined.is_sp_framework_required,
        combined.number_months,
        combined.oversight_agency,
        combined.ready_for_certification_date,
        combined.sp_framework_basis,
        combined.sp_framework_opinions,
        combined.submitted_date,
        combined.total_amount_expended,
        combined.type_audit_code,
        combined.additional_award_identification,
        combined.amount_expended,
        combined.cluster_name,
        combined.cluster_total,
        combined.federal_agency_prefix,
        combined.federal_award_extension,
        combined.federal_program_name,
        combined.federal_program_total,
        combined.findings_count,
        combined.is_direct,
        combined.is_loan,
        combined.is_major,
        combined.is_passthrough_award,
        combined.loan_balance,
        combined.audit_report_type,
        combined.other_cluster_name,
        combined.passthrough_amount,
        combined.state_cluster_name,
        combined.is_material_weakness,
        combined.is_modified_opinion,
        combined.is_other_findings,
        combined.is_other_matters,
        combined.is_questioned_costs,
        combined.is_repeat_finding,
        combined.is_significant_deficiency,
        combined.prior_finding_ref_numbers,
        combined.type_requirement,
        combined.passthrough_name,
        combined.passthrough_id
    from
        dissemination_combined combined
    where
        (combined.is_public = true
        or (combined.is_public = false and api_v1_1_1_functions.has_tribal_data_access()))
    order by combined.id
;

commit;

notify pgrst,
       'reload schema';

