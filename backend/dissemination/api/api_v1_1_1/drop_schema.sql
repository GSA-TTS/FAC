
begin;

DROP SCHEMA IF EXISTS api_v1_1_1 CASCADE;
-- DROP ROLE IF EXISTS authenticator;
-- DROP ROLE IF EXISTS api_fac_gov;

commit;

notify pgrst,
       'reload schema';