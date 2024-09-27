BEGIN;
    --
    -- This drops all the views, too.
    ---
    DROP SCHEMA IF EXISTS public_api_v2_0_0_alpha CASCADE;
COMMIT;

notify pgrst,
       'reload schema';
