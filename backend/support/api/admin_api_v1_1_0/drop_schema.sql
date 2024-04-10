
begin;

DROP SCHEMA IF EXISTS admin_api_v1_1_0 CASCADE;

commit;

notify pgrst,
       'reload schema';
