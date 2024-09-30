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

---------------------------------------
-- combined
---------------------------------------
CREATE VIEW public_api_v2_0_0_alpha.combined AS
    SELECT * FROM public_data_v1_0_0.combined comb
    ;



COMMIT;

notify pgrst,
       'reload schema';
