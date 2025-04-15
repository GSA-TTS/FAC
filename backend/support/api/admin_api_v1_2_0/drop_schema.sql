
begin;

DROP SCHEMA IF EXISTS admin_api_v1_2_0 CASCADE;
DROP SCHEMA IF EXISTS admin_api_v1_2_0_functions CASCADE;
DROP SCHEMA IF EXISTS admin_api_v1_2_0 CASCADE;

commit;

notify pgrst,
       'reload schema';
