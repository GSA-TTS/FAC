begin;

do
$$
BEGIN
    DROP SCHEMA IF EXISTS public_api_v2_0_0_alpha CASCADE;
    DROP SCHEMA IF EXISTS public_api_v2_0_0_alpha_functions CASCADE;

    CREATE SCHEMA IF NOT EXISTS public_api_v2_0_0_alpha;
    CREATE SCHEMA IF NOT EXISTS public_api_v2_0_0_alpha_functions;
        
    GRANT USAGE ON SCHEMA public_api_v2_0_0_alpha_functions TO api_fac_gov;

    -- Grant access to tables and views
    ALTER DEFAULT PRIVILEGES
        IN SCHEMA public_api_v2_0_0_alpha
        GRANT SELECT
    -- this includes views
    ON tables
    TO api_fac_gov;

    -- Grant access to sequences, if we have them
    GRANT USAGE ON SCHEMA public_api_v2_0_0_alpha to api_fac_gov;
    GRANT SELECT, USAGE 
    ON ALL SEQUENCES 
    IN SCHEMA public_api_v2_0_0_alpha 
    TO api_fac_gov;
    
    -- ALTER DEFAULT PRIVILEGES
    --     IN SCHEMA public_api_v2_0_0_alpha
    --     GRANT SELECT, USAGE
    -- ON sequences
    -- TO api_fac_gov;
END
$$
;

COMMIT;

notify pgrst,
       'reload schema';

