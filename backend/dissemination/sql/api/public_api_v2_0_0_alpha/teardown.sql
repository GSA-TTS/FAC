BEGIN;
    --
    -- This drops all the views, too.
    ---
    DROP SCHEMA IF EXISTS public_api_v2_0_0_alpha CASCADE;
    DROP SCHEMA IF EXISTS public_api_v2_0_0_alpha_functions CASCADE;

COMMIT;

notify pgrst,
       'reload schema';
