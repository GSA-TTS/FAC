-----------------------
-- AUDIT CURATION
-- This disables curation tracking on the below tables.
-- We do this at startup *just in case* the app crashed while we were
-- doing data curation. If that were true, the DB would be recording 
-- EVERY change to these two tables. Given that the `singleauditchecklist` 
-- table is hit *constantly*, this would be bad.
--
-- Therefore, one of the first things we do every time we startup is 
-- make sure that this state is disabled in the database.

select curation.disable_tracking('public.audit_singleauditchecklist'::regclass);
select curation.disable_tracking('public.support_cognizantassignment'::regclass);
