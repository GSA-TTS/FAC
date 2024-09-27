
begin;

DROP SCHEMA IF EXISTS public_api_v2_0_0_alpha CASCADE;

-- DROP ROLE IF EXISTS authenticator;
-- DROP ROLE IF EXISTS api_fac_gov;

commit;

notify pgrst,
       'reload schema';
