
begin;

DROP SCHEMA IF EXISTS admin_api_v1_1_0 CASCADE;

commit;

notify pgrst,
       'reload schema';
begin;

    drop view if exists admin_api_v1_1_0.audit_access;
    
commit;

notify pgrst,
       'reload schema';
