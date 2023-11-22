begin;

do
$$
begin
    DROP SCHEMA IF EXISTS admin_api_v1_0_0 CASCADE;

    if not exists (select schema_name from information_schema.schemata where schema_name = 'admin_api_v1_0_0') then
        create schema admin_api_v1_0_0;

        -- Grant access to tables and views
        alter default privileges
            in schema admin_api_v1_0_0
            grant select
        -- this includes views
        on tables
        to api_fac_gov;

        -- Grant access to sequences, if we have them
        grant usage on schema admin_api_v1_0_0 to api_fac_gov;
        grant select, usage on all sequences in schema admin_api_v1_0_0 to api_fac_gov;
        alter default privileges
            in schema admin_api_v1_0_0
            grant select, usage
        on sequences
        to api_fac_gov;
    end if;
end
$$
;

commit;

notify pgrst,
       'reload schema';

