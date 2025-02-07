
begin;

DROP SCHEMA IF EXISTS api_v2_0_0 CASCADE;
-- DROP ROLE IF EXISTS authenticator;
-- DROP ROLE IF EXISTS api_fac_gov;

commit;

notify pgrst,
       'reload schema';
