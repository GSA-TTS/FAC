
BEGIN;

DROP SCHEMA IF EXISTS admin_api_v1_1_1 CASCADE;

COMMIT;

notify pgrst, 'reload schema';
