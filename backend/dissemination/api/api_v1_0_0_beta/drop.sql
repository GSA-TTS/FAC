
begin;

DROP SCHEMA IF EXISTS api_v1_0_0_beta CASCADE; 

commit;

notify pgrst,
       'reload schema';

