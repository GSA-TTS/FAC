begin;

    drop table if exists admin_api_v1_0_0.audit_access;
    
commit;

notify pgrst,
       'reload schema';
