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

NOTIFY pgrst, 'reload schema';
begin;

do
$$
begin
    DROP SCHEMA IF EXISTS api_v1_1_0 CASCADE;
    DROP SCHEMA IF EXISTS api_v1_1_0_functions CASCADE;

    if not exists (select schema_name from information_schema.schemata where schema_name = 'api_v1_1_0') then
        create schema api_v1_1_0;
        create schema api_v1_1_0_functions;
        
        grant usage on schema api_v1_1_0_functions to api_fac_gov;
        grant usage on schema api_v1_1_0 to api_fac_gov;
        grant select, usage on all sequences in schema api_v1_1_0 to api_fac_gov;

        -- Grant access to tables and views
        -- NOTE 20240920: This grants SELECT to all tables
        -- created in this schema *in the future*. Nothing
        -- that already exists is affected.
        -- https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html
        alter default privileges
            in schema api_v1_1_0
            grant select
        -- this includes views
        on tables
        to api_fac_gov;

        alter default privileges
            in schema api_v1_1_0_functions
            grant select
            -- this includes views
            on tables
            to api_fac_gov;

        -- Grant access to future sequences, if we have them
        alter default privileges
            in schema api_v1_1_0
            grant select, usage
            on sequences
            to api_fac_gov;

    end if;
end
$$
;

-- https://postgrest.org/en/stable/references/api/openapi.html
-- This is the title (version number) and description (text).
COMMENT ON SCHEMA api_v1_1_0 IS
$$v1.1.0

A RESTful API that serves data from the SF-SAC.$$;


commit;

notify pgrst,
       'reload schema';

-- WARNING
-- Under PostgreSQL 12, the functions below work.
-- Under PostgreSQL 14, these will break.
--
-- Note the differences:
--
-- raise info 'Works under PostgreSQL 12';
-- raise info 'request.header.x-magic %', (SELECT current_setting('request.header.x-magic', true));
-- raise info 'request.jwt.claim.expires %', (SELECT current_setting('request.jwt.claim.expires', true));
-- raise info 'Works under PostgreSQL 14';
-- raise info 'request.headers::json->>x-magic %', (SELECT current_setting('request.headers', true)::json->>'x-magic');
-- raise info 'request.jwt.claims::json->expires %', (SELECT current_setting('request.jwt.claims', true)::json->>'expires');
--
-- To quote the work of Dav Pilkey, "remember this now."


CREATE OR REPLACE FUNCTION api_v1_1_0_functions.get_header(item text) RETURNS text
    AS $get_header$
    declare res text;
   	begin
    	SELECT (current_setting('request.headers', true)::json)->>item into res;
    	return res;
   end;
$get_header$ LANGUAGE plpgsql;

create or replace function api_v1_1_0_functions.get_api_key_uuid() returns TEXT
as $gaku$
declare uuid text;
begin
	select api_v1_1_0_functions.get_header('x-api-user-id') into uuid;
	return uuid;
end;
$gaku$ LANGUAGE plpgsql;

create or replace function api_v1_1_0_functions.has_tribal_data_access() 
returns boolean
as $has_tribal_data_access$
DECLARE 
    uuid_header UUID;
    key_exists boolean;
BEGIN

    SELECT api_v1_1_0_functions.get_api_key_uuid() INTO uuid_header;
    SELECT 
        CASE WHEN EXISTS (
            SELECT key_id 
            FROM public.dissemination_TribalApiAccessKeyIds taaki
            WHERE taaki.key_id = uuid_header::TEXT)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;
    RAISE INFO 'api_v1_1_0 has_tribal % %', uuid_header, key_exists;
    RETURN key_exists;
END;
$has_tribal_data_access$ LANGUAGE plpgsql;

-- If you change the constant defined by this function,
-- you must regenerate the index.
CREATE OR REPLACE FUNCTION api_v1_1_0_functions.batch_size()
  RETURNS int
  LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
'SELECT 20000';
GRANT EXECUTE ON FUNCTION api_v1_1_0_functions.batch_size() TO api_fac_gov;

CREATE OR REPLACE FUNCTION api_v1_1_0_functions.batch (id bigint) 
returns bigint 
as $batch$
declare num bigint;
begin
    select div(id, api_v1_1_0_functions.batch_size()) into num;
    return num;
end;
$batch$
language plpgsql immutable;
GRANT EXECUTE ON FUNCTION api_v1_1_0_functions.batch(bigint) TO api_fac_gov;

CREATE OR REPLACE FUNCTION api_v1_1_0.batches (in_table text) 
returns integer 
as $batches$
declare count integer;
declare batch_size bigint;
begin 
    select api_v1_1_0_functions.batch_size() into batch_size;
	case
	   	when in_table = 'general' then  
	   		select div(count(*), batch_size) into count 
	   		from public.dissemination_general;
	   	when in_table = 'federal_awards' then  
	   		select div(count(*), batch_size) into count 
	   		from public.dissemination_federalaward;
	else
		count := 0;
	end case;
	RETURN count;
end;
$batches$   
language plpgsql;
GRANT EXECUTE ON FUNCTION api_v1_1_0.batches(text) TO api_fac_gov;

CREATE OR REPLACE FUNCTION api_v1_1_0.get_general_batch (batch_no bigint) 
returns setof dissemination_general
as $batches$
	select  * from public.dissemination_general where api_v1_1_0_functions.batch(id) = batch_no;
$batches$   
language sql;
GRANT EXECUTE ON FUNCTION api_v1_1_0.get_general_batch(bigint) TO api_fac_gov;

CREATE OR REPLACE FUNCTION api_v1_1_0.get_federal_award_batch (batch_no bigint) 
returns setof dissemination_federalaward
as $batches$
	select  * from public.dissemination_federalaward where api_v1_1_0_functions.batch(public.dissemination_federalaward.id) = batch_no;
$batches$   
language sql;
GRANT EXECUTE ON FUNCTION api_v1_1_0.get_federal_award_batch(bigint) TO api_fac_gov;


-- We should consider dropping and regenerating this index
-- every night after MV generation.
-- drop index batch_by_id_dfa;
create index IF NOT EXISTS batch_by_id_dfa 
    on public.dissemination_federalaward 
    using btree(api_v1_1_0_functions.batch(public.dissemination_federalaward.id));


NOTIFY pgrst, 'reload schema';
begin;

---------------------------------------
-- finding_text
---------------------------------------
create view api_v1_1_0.findings_text as
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
        or (gen.is_public = false and api_v1_1_0_functions.has_tribal_data_access()))
    order by ft.id
;

---------------------------------------
-- additional_ueis
---------------------------------------
create view api_v1_1_0.additional_ueis as
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
create view api_v1_1_0.findings as
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
create view api_v1_1_0.federal_awards as
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
create view api_v1_1_0.corrective_action_plans as
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
        or (gen.is_public = false and api_v1_1_0_functions.has_tribal_data_access()))
    order by ct.id
;

---------------------------------------
-- notes_to_sefa
---------------------------------------
create view api_v1_1_0.notes_to_sefa as
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
        or (gen.is_public = false and api_v1_1_0_functions.has_tribal_data_access()))
    order by note.id
;

---------------------------------------
-- passthrough
---------------------------------------
create view api_v1_1_0.passthrough as
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
create view api_v1_1_0.general as
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
create view api_v1_1_0.secondary_auditors as
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

create view api_v1_1_0.additional_eins as
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

