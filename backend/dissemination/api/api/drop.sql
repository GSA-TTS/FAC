
begin;

DROP SCHEMA IF EXISTS api CASCADE; 

commit;

notify pgrst,
       'reload schema';

