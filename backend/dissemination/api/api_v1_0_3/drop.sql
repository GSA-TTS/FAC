
begin;

DROP SCHEMA IF EXISTS api_v1_0_3 CASCADE;

--We can't drop these due to cascading issues during teardown and setup.
-- DROP ROLE IF EXISTS authenticator;
-- DROP ROLE IF EXISTS api_fac_gov;

commit;

notify pgrst,
       'reload schema';
