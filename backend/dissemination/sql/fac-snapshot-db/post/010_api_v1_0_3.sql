------------------------------------------------------------------
-- GATE
------------------------------------------------------------------
-- We only want the API to run if certain conditions are met.
-- We could try and encode that in the `bash` portion of the code.
-- Or, we could just gate things at the top of our SQL. 
-- If the conditions are not met, we should exit noisily.
-- A cast to regclass will fail with an exception if the table
-- does not exist.
DO LANGUAGE plpgsql
$GATE$
    DECLARE
        the_schema varchar := 'public';
        the_table  varchar := 'dissemination_general';
        api_ver    varchar := 'API_v1_0_3';
    BEGIN
        IF EXISTS (
            SELECT FROM pg_tables
            WHERE  schemaname = the_schema
            AND    tablename  = the_table
            )
        THEN
            RAISE info '% Gate condition met. Continuing.', api_ver;
        ELSE
            RAISE exception '% %.% not found.', api_ver, the_schema, the_table;
        END IF;
    END
$GATE$;

SELECT 'public.dissemination_general'::regclass;

DO
$APIV103$
    BEGIN
        DROP SCHEMA IF EXISTS api_v1_0_3 CASCADE;
        DROP SCHEMA IF EXISTS api_v1_0_3_functions CASCADE;

        IF NOT EXISTS (select schema_name 
                        from information_schema.schemata 
                        where schema_name = 'api_v1_0_3') then
            CREATE SCHEMA api_v1_0_3;
            CREATE SCHEMA api_v1_0_3_functions;
            
            GRANT USAGE ON SCHEMA api_v1_0_3_functions to api_fac_gov;

            -- Grant access to tables and views
            alter default privileges
                in schema api_v1_0_3
                grant select
            -- this includes views
            on tables
            to api_fac_gov;

            -- Grant access to sequences, if we have them
            grant usage on schema api_v1_0_3 to api_fac_gov;
            grant select, usage on all sequences in schema api_v1_0_3 to api_fac_gov;
            alter default privileges
                in schema api_v1_0_3
                grant select, usage
            on sequences
            to api_fac_gov;
        end if;
    END
$APIV103$
;

------------------------------------------------------------------
-- functions
------------------------------------------------------------------
create or replace function api_v1_0_3_functions.has_tribal_data_access() returns boolean
as $has_tribal_data_access$
BEGIN
    RETURN 0::BOOLEAN;
END;
$has_tribal_data_access$ LANGUAGE plpgsql;

------------------------------------------------------------------
-- VIEWs
------------------------------------------------------------------
---------------------------------------
-- finding_text
---------------------------------------
create view api_v1_0_3.findings_text as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ft.finding_ref_number,
        ft.contains_chart_or_table,
        ft.finding_text
    from
        public.dissemination_findingtext ft,
        public.dissemination_general gen
    where
        ft.report_id = gen.report_id
         and
        (gen.is_public = true
         or 
        (gen.is_public = false and api_v1_0_3_functions.has_tribal_data_access()))
    order by ft.id
;

---------------------------------------
-- additional_ueis
---------------------------------------
create view api_v1_0_3.additional_ueis as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        uei.additional_uei
    from
        public.dissemination_general gen,
        public.dissemination_additionaluei uei
    where
        gen.report_id = uei.report_id
         and
        (gen.is_public = true
         or 
        (gen.is_public = false and api_v1_0_3_functions.has_tribal_data_access()))
    order by uei.id
;

---------------------------------------
-- finding
---------------------------------------
create view api_v1_0_3.findings as
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
        public.dissemination_finding finding,
        public.dissemination_general gen
    where
        finding.report_id = gen.report_id
         and
        (gen.is_public = true
         or 
        (gen.is_public = false and api_v1_0_3_functions.has_tribal_data_access()))
    order by finding.id
;

---------------------------------------
-- federal award
---------------------------------------
create view api_v1_0_3.federal_awards as
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
        public.dissemination_federalaward award,
        public.dissemination_general gen
    where
        award.report_id = gen.report_id
         and
        (gen.is_public = true
         or 
        (gen.is_public = false and api_v1_0_3_functions.has_tribal_data_access()))
    order by award.id
;


---------------------------------------
-- corrective_action_plan
---------------------------------------
create view api_v1_0_3.corrective_action_plans as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        ct.finding_ref_number,
        ct.contains_chart_or_table,
        ct.planned_action
    from
        public.dissemination_CAPText ct,
        public.dissemination_General gen
    where
        ct.report_id = gen.report_id
         and
        (gen.is_public = true
         or 
        (gen.is_public = false and api_v1_0_3_functions.has_tribal_data_access()))
    order by ct.id
;

---------------------------------------
-- notes_to_sefa
---------------------------------------
create view api_v1_0_3.notes_to_sefa as
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
        public.dissemination_general gen,
        public.dissemination_note note
    where
        note.report_id = gen.report_id
         and
        (gen.is_public = true
         or 
        (gen.is_public = false and api_v1_0_3_functions.has_tribal_data_access()))
    order by note.id
;

---------------------------------------
-- passthrough
---------------------------------------
create view api_v1_0_3.passthrough as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        pass.award_reference,
        pass.passthrough_id,
        pass.passthrough_name
    from
        public.dissemination_general as gen,
        public.dissemination_passthrough as pass
    where
        gen.report_id = pass.report_id
        and
        (gen.is_public = true
        or 
        (gen.is_public = false and api_v1_0_3_functions.has_tribal_data_access()))
    order by pass.id
;


---------------------------------------
-- general
---------------------------------------
create view api_v1_0_3.general as
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
        public.dissemination_general gen
    where
        gen.is_public = true
         or 
        (gen.is_public = false and api_v1_0_3_functions.has_tribal_data_access())
    order by gen.id
;

---------------------------------------
-- auditor (secondary auditor)
---------------------------------------
create view api_v1_0_3.secondary_auditors as
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
        public.dissemination_General gen,
        public.dissemination_SecondaryAuditor sa
    where
        sa.report_id = gen.report_id
         and
        (gen.is_public=True
         or 
        (gen.is_public=false and api_v1_0_3_functions.has_tribal_data_access()))
    order by sa.id
;

create view api_v1_0_3.additional_eins as
    select
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        ---
        ein.additional_ein
    from
        public.dissemination_general gen,
        public.dissemination_additionalein ein
    where
        gen.report_id = ein.report_id
         and
        (gen.is_public = true
         or 
        (gen.is_public = false and api_v1_0_3_functions.has_tribal_data_access()))
    order by ein.id
;