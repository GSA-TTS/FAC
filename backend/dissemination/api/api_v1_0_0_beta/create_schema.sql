-- Cloned from Lindsay's code in data_distro

-- We are self managing our migrations here
-- The SQL is called and applied from data_distro/migrations
-- This is a point in time of sql run that is comparable with data distro models. The views in the api_v1_0_0-beta_views folder represent the current views for the API_V1_0_0-BETA.
-- As the models change later, we don't want
-- our migration to reference fields that don't exist yet or already exist.

--This will be used by the postgrest API_V1_0_0-BETA

begin;

-- These need to be if statements because the schema and rolls already exist when you run tests
do
$$
begin
    if not exists (select * from pg_catalog.pg_roles where rolname = 'anon') then
        create role anon;
    end if;
end
$$
;

do
$$
begin
    if not exists (select schema_name from information_schema.schemata where schema_name = 'api_v1_0_0_beta') then
        create schema api_v1_0_0_beta;

        -- Grant access to tables and views
        alter default privileges
            in schema api_v1_0_0_beta
            grant select
        -- this includes views
        on tables
        to anon;

        -- Grant access to sequences, if we have them
        grant usage on schema api_v1_0_0_beta to anon;
        grant select, usage on all sequences in schema api_v1_0_0_beta to anon;
        alter default privileges
            in schema api_v1_0_0_beta
            grant select, usage
        on sequences
        to anon;
    end if;
end
$$
;

commit;

notify pgrst,
       'reload schema';

