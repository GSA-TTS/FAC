begin;

    drop view if exists admin_api_v2_0_0.audit_access;
    
commit;

notify pgrst,
       'reload schema';
