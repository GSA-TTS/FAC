DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'authenticator') THEN
      RAISE NOTICE 'Role "authenticator" already exists. Skipping.';
   ELSE
      CREATE ROLE authenticator LOGIN NOINHERIT NOCREATEDB NOCREATEROLE NOSUPERUSER;
   END IF;
END
$do$;

DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'api_fac_gov') THEN
      RAISE NOTICE 'Role "api_fac_gov" already exists. Skipping.';
   ELSE
      CREATE ROLE api_fac_gov NOLOGIN;
   END IF;
END
$do$;

GRANT api_fac_gov TO authenticator;

CREATE SEQUENCE IF NOT EXISTS public_data_general
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE;


NOTIFY pgrst, 'reload schema';
begin;

do
$$
BEGIN
    DROP SCHEMA IF EXISTS public_api_v2_0_0_alpha CASCADE;
    DROP SCHEMA IF EXISTS public_api_v2_0_0_alpha_functions CASCADE;

    CREATE SCHEMA IF NOT EXISTS public_api_v2_0_0_alpha;
    CREATE SCHEMA IF NOT EXISTS public_api_v2_0_0_alpha_functions;
        
    GRANT USAGE ON SCHEMA public_api_v2_0_0_alpha_functions TO api_fac_gov;

    -- Grant access to tables and views
    ALTER DEFAULT PRIVILEGES
        IN SCHEMA public_api_v2_0_0_alpha
        GRANT SELECT
    -- this includes views
    ON tables
    TO api_fac_gov;

    -- Grant access to sequences, if we have them
    GRANT USAGE ON SCHEMA public_api_v2_0_0_alpha to api_fac_gov;
    GRANT SELECT, USAGE 
    ON ALL SEQUENCES 
    IN SCHEMA public_api_v2_0_0_alpha 
    TO api_fac_gov;
    
    -- ALTER DEFAULT PRIVILEGES
    --     IN SCHEMA public_api_v2_0_0_alpha
    --     GRANT SELECT, USAGE
    -- ON sequences
    -- TO api_fac_gov;
END
$$
;

COMMIT;

notify pgrst,
       'reload schema';

-- Under the new approach, we don't need 
-- any functions here.

NOTIFY pgrst, 'reload schema';
BEGIN;

CREATE VIEW public_api_v2_0_0_alpha.additional_eins AS
    SELECT * FROM public_data_v1_0_0.additional_eins ae
    ORDER BY ae.id
;

---------------------------------------
-- additional_ueis
---------------------------------------
create view public_api_v2_0_0_alpha.additional_ueis AS
    SELECT * FROM public_data_v1_0_0.additional_ueis au
    ORDER BY au.id
;

---------------------------------------
-- corrective_action_plan
---------------------------------------
CREATE VIEW public_api_v2_0_0_alpha.corrective_action_plans AS
    SELECT * FROM public_data_v1_0_0.corrective_action_plans cap
    ORDER BY cap.id
;

---------------------------------------
-- finding
---------------------------------------
CREATE VIEW public_api_v2_0_0_alpha.findings as
    SELECT * FROM public_data_v1_0_0.findings f
    ORDER BY f.id
;

---------------------------------------
-- finding_text
---------------------------------------
CREATE VIEW public_api_v2_0_0_alpha.findings_text AS
    SELECT * FROM public_data_v1_0_0.findings_text ft
    ORDER BY ft.id
;

---------------------------------------
-- federal award
---------------------------------------
CREATE VIEW public_api_v2_0_0_alpha.federal_awards AS
    SELECT * FROM public_data_v1_0_0.federal_awards fa
    ORDER BY fa.id
;

---------------------------------------
-- general
---------------------------------------
CREATE VIEW public_api_v2_0_0_alpha.general AS
    SELECT * FROM public_data_v1_0_0.general
;

---------------------------------------
-- notes_to_sefa
---------------------------------------
create view public_api_v2_0_0_alpha.notes_to_sefa AS
    SELECT * FROM public_data_v1_0_0.notes_to_sefa nts
    ORDER BY nts.id
;

---------------------------------------
-- passthrough
---------------------------------------
CREATE VIEW public_api_v2_0_0_alpha.passthrough AS
    SELECT * FROM public_data_v1_0_0.passthrough p
    ORDER BY p.id
;


---------------------------------------
-- auditor (secondary auditor)
---------------------------------------
CREATE VIEW public_api_v2_0_0_alpha.secondary_auditors AS
    SELECT * FROM public_data_v1_0_0.secondary_auditors sa
    ORDER BY sa.id
    ;

-- Specify every field in dissemination_combined, omitting the id.
-- Generated fields like ALN are done in the creation of the table, not here.
-- create view public_api_v2_0_0_alpha.combined as
--     select
--         combined.report_id,
--         combined.award_reference,
--         combined.reference_number,
--         combined.aln,
--         combined.agencies_with_prior_findings,
--         combined.audit_period_covered,
--         combined.audit_type,
--         combined.audit_year,
--         combined.auditee_address_line_1,
--         combined.auditee_certified_date,
--         combined.auditee_certify_name,
--         combined.auditee_certify_title,
--         combined.auditee_city,
--         combined.auditee_contact_name,
--         combined.auditee_contact_title,
--         combined.auditee_ein,
--         combined.auditee_email,
--         combined.auditee_name,
--         combined.auditee_phone,
--         combined.auditee_state,
--         combined.auditee_uei,
--         combined.auditee_zip,
--         combined.auditor_address_line_1,
--         combined.auditor_certified_date,
--         combined.auditor_certify_name,
--         combined.auditor_certify_title,
--         combined.auditor_city,
--         combined.auditor_contact_name,
--         combined.auditor_contact_title,
--         combined.auditor_country,
--         combined.auditor_ein,
--         combined.auditor_email,
--         combined.auditor_firm_name,
--         combined.auditor_foreign_address,
--         combined.auditor_phone,
--         combined.auditor_state,
--         combined.auditor_zip,
--         combined.cognizant_agency,
--         combined.data_source,
--         combined.date_created,
--         combined.dollar_threshold,
--         combined.entity_type,
--         combined.fac_accepted_date,
--         combined.fy_end_date,
--         combined.fy_start_date,
--         combined.gaap_results,
--         combined.is_additional_ueis,
--         combined.is_aicpa_audit_guide_included,
--         combined.is_going_concern_included,
--         combined.is_internal_control_deficiency_disclosed,
--         combined.is_internal_control_material_weakness_disclosed,
--         combined.is_low_risk_auditee,
--         combined.is_material_noncompliance_disclosed,
--         combined.is_public,
--         combined.is_sp_framework_required,
--         combined.number_months,
--         combined.oversight_agency,
--         combined.ready_for_certification_date,
--         combined.sp_framework_basis,
--         combined.sp_framework_opinions,
--         combined.submitted_date,
--         combined.total_amount_expended,
--         combined.type_audit_code,
--         combined.additional_award_identification,
--         combined.amount_expended,
--         combined.cluster_name,
--         combined.cluster_total,
--         combined.federal_agency_prefix,
--         combined.federal_award_extension,
--         combined.federal_program_name,
--         combined.federal_program_total,
--         combined.findings_count,
--         combined.is_direct,
--         combined.is_loan,
--         combined.is_major,
--         combined.is_passthrough_award,
--         combined.loan_balance,
--         combined.audit_report_type,
--         combined.other_cluster_name,
--         combined.passthrough_amount,
--         combined.state_cluster_name,
--         combined.is_material_weakness,
--         combined.is_modified_opinion,
--         combined.is_other_findings,
--         combined.is_other_matters,
--         combined.is_questioned_costs,
--         combined.is_repeat_finding,
--         combined.is_significant_deficiency,
--         combined.prior_finding_ref_numbers,
--         combined.type_requirement,
--         combined.passthrough_name,
--         combined.passthrough_id
--     from
--         dissemination_combined combined
--     where
--         (combined.is_public = true
--         or (combined.is_public = false and public_api_v2_0_0_alpha_functions.has_tribal_data_access()))
--     order by combined.id
-- ;

COMMIT;

notify pgrst,
       'reload schema';
