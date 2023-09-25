-- This schema is handled external to the app.
-- Why?
-- It relies on static tables that are loaded before the app exists.
-- Therefore, we assume those tables are loaded. Or, mostly assume.
-- This grants permissions, nothing more.

begin;

do
$$
begin
    -- If it exists, grant permissions.
    if exists (select schema_name from information_schema.schemata where schema_name = 'api_historic_v0_1_0_alpha') then
        -- Grant access to tables and views
        alter default privileges
            in schema api_historic_v0_1_0_alpha
            grant select
        -- this includes views
        on tables
        to api_fac_gov;

        -- Grant access to sequences, if we have them
        grant usage on schema api_historic_v0_1_0_alpha to api_fac_gov;
        grant select, usage on all sequences in schema api_historic_v0_1_0_alpha to api_fac_gov;
        alter default privileges
            in schema api_historic_v0_1_0_alpha
            grant select, usage
        on sequences
        to api_fac_gov;

        GRANT SELECT ON ALL TABLES IN SCHEMA api_historic_v0_1_0_alpha TO api_fac_gov;
    end if;
end
$$
;

select 1;

commit;

notify pgrst, 'reload schema';

