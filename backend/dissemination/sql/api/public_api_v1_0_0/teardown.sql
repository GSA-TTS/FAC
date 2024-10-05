BEGIN;
    --
    -- This drops all the views, too.
    ---
    DROP SCHEMA IF EXISTS public_api_v1_0_0 CASCADE;
    DROP SCHEMA IF EXISTS public_api_v1_0_0_functions CASCADE;

COMMIT;


notify pgrst,
       'reload schema';
