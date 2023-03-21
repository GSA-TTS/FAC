-- run by data/distro/migrations/0030_add_api_views.py

-- We are self managing our migrations here
-- The SQL is called and applied from data_distro/migrations
-- This is a point in time of sql run that is comparable with data distro models. The views in the api_views folder represent the current views for the API.
-- As the models change later, we don't want
-- our migration to reference fields that don't exist yet or already exist.

begin;

--This will be used by the postgrest API
drop role if exists anon;
create role anon nologin;
create schema api;

-- Grant access to tables and views
alter default privileges
    in schema api
    grant select
-- this includes views
on tables
to anon;

-- Grant access to sequences, if we have them
grant select, usage on all sequences in schema api to anon;
alter default privileges
    in schema api
    grant select, usage
on sequences
to anon;

commit;
