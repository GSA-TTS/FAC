begin;

do
$$
begin
    DROP SCHEMA IF EXISTS admin_api_v2_0_0 CASCADE;
    DROP SCHEMA IF EXISTS admin_api_v2_0_0_functions CASCADE;

    if not exists (select schema_name from information_schema.schemata where schema_name = 'admin_api_v2_0_0') then
        create schema admin_api_v2_0_0;
        create schema admin_api_v2_0_0_functions;

        grant usage on schema admin_api_v2_0_0_functions to api_fac_gov;

        -- Grant access to tables and views
        alter default privileges
            in schema admin_api_v2_0_0
            grant select
        -- this includes views
        on tables
        to api_fac_gov;
                
        -- Grant access to sequences, if we have them
        grant usage on schema admin_api_v2_0_0 to api_fac_gov;
        grant select, usage on all sequences in schema admin_api_v2_0_0 to api_fac_gov;
        alter default privileges
            in schema admin_api_v2_0_0
            grant select, usage
        on sequences
        to api_fac_gov;

        -- The admin API needs to be able to write user permissions.
        -- This is so we can add and remove people who will have tribal data access
        -- via the administrative API.
        GRANT INSERT, SELECT, DELETE on public.users_userpermission to api_fac_gov;
        -- We need to be able to look up slugs and turn them into permission IDs.
        GRANT SELECT on public.users_permission to api_fac_gov;
        -- It also needs to be able to log events.
        GRANT INSERT on public.support_adminapievent to api_fac_gov;
        -- And, it wants to read the UUIDs of administrative keys
        GRANT SELECT ON public.support_administrative_key_uuids TO api_fac_gov;
        -- We want to see data in flight as admins.
        GRANT SELECT ON public.audit_singleauditchecklist TO api_fac_gov;
        GRANT SELECT ON public.audit_access TO api_fac_gov;
        GRANT SELECT ON public.audit_excelfile TO api_fac_gov;
        GRANT SELECT ON public.audit_singleauditreportfile TO api_fac_gov;
        GRANT SELECT ON public.audit_submissionevent TO api_fac_gov;
        GRANT SELECT ON public.auth_user TO api_fac_gov;
        GRANT SELECT ON public.django_migrations TO api_fac_gov;
        GRANT SELECT ON public.support_cognizantassignment TO api_fac_gov;
        GRANT SELECT ON public.support_cognizantbaseline TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_elecauditfindings TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_elecauditheader_ims TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_elecauditheader TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_elecaudits TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_eleccaptext TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_eleccpas TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_eleceins TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_elecfindingstext TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_elecnotes TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_elecpassthrough TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_elecrpt_revisions TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_elecueis TO api_fac_gov;
        GRANT SELECT ON public.census_historical_migration_federalagencylookup TO api_fac_gov;
        -- The curation record is not on public.
        GRANT SELECT ON curation.record_version TO api_fac_gov;


        GRANT INSERT, SELECT, DELETE on public.dissemination_tribalapiaccesskeyids to api_fac_gov;
        GRANT INSERT on public.dissemination_onetimeaccess to api_fac_gov;
    end if;
end
$$
;

commit;

notify pgrst,
       'reload schema';

