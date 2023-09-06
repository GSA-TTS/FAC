
begin;

DROP SCHEMA IF EXISTS api_v1_0_0_beta CASCADE; 
-- DROP ROLE IF EXISTS authenticator;
-- DROP ROLE IF EXISTS api_fac_gov;

commit;

notify pgrst,
       'reload schema';
