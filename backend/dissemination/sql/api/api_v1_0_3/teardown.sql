BEGIN;
    DROP SCHEMA IF EXISTS api_v1_0_3 CASCADE;
COMMIT;

NOTIFY pgrst, 'reload schema';
