
begin;

DROP SCHEMA IF EXISTS admin_api_v2_0_0 CASCADE;

commit;

notify pgrst,
       'reload schema';
