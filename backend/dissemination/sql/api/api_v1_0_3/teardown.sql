BEGIN;
    -- This wipes out the schema and all attached objects,
    -- including all of our views.
    DROP SCHEMA IF EXISTS api_v1_0_3 CASCADE;
COMMIT;

NOTIFY pgrst, 'reload schema';
