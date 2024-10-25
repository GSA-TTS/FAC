---------------------------------
-- DROP
---------------------------------
DROP SCHEMA IF EXISTS api_v1_0_3 CASCADE;
DROP SCHEMA IF EXISTS api_v1_1_0 CASCADE;
DROP SCHEMA IF EXISTS api_v1_1_1 CASCADE;

DROP SCHEMA IF EXISTS admin_api_v1_1_0 CASCADE;
DROP SCHEMA IF EXISTS admin_api_v1_1_0_functions CASCADE;

DROP SCHEMA IF EXISTS admin_api_v1_1_1 CASCADE;
DROP SCHEMA IF EXISTS admin_api_v1_1_1_functions CASCADE;

DROP SCHEMA IF EXISTS api_v2_0_0 CASCADE;
DROP SCHEMA IF EXISTS api_v2_0_0_functions CASCADE;

-------------
-- ALWAYS
-- This is the start of the pipeline.
-- It is a copy of the backed up dissemination tables in
-- fac-snapshot-db. Always drop the schema and make a new copy.
-------------
DROP SCHEMA IF EXISTS dissem_copy CASCADE;

------------------------------------------------------------------
-- CONDITIONAL
------------------------------------------------------------------
-- On deploys, we don't want to tear down the public data.
-- So, we check to see if the metadata table is present, and if so, 
-- leave the schemas in place.
DO LANGUAGE plpgsql
$GATE$
    DECLARE
        the_schema varchar := 'public_data_v1_0_0';
        the_table  varchar := 'metadata';
    BEGIN
        IF EXISTS (
            SELECT FROM pg_tables
            WHERE  schemaname = the_schema
            AND    tablename  = the_table
            )
        THEN
            RAISE info 'The metadata table exists; leaving public data schemas in place.';
        ELSE
            RAISE info 'The metadata table does not exist; dropping schemas for a clean rebuild.';
            DROP SCHEMA IF EXISTS public_data_v1_0_0 CASCADE;
            DROP SCHEMA IF EXISTS suppressed_data_v1_0_0 CASCADE;
        END IF;
    END
$GATE$;

---------------------------------
-- CREATE
---------------------------------
-- Retired 20241024
-- CREATE SCHEMA IF NOT EXISTS api_v1_0_3;
-- CREATE SCHEMA IF NOT EXISTS api_v1_0_3_functions;

CREATE SCHEMA IF NOT EXISTS api_v1_1_0;
CREATE SCHEMA IF NOT EXISTS api_v1_1_0_functions;

-- Retired 20241024
-- CREATE SCHEMA IF NOT EXISTS admin_api_v1_1_0;
-- CREATE SCHEMA IF NOT EXISTS admin_api_v1_1_0_functions;

CREATE SCHEMA IF NOT EXISTS public_data_v1_0_0;
CREATE SCHEMA IF NOT EXISTS public_data_v1_0_0_functions;
CREATE SCHEMA IF NOT EXISTS suppressed_data_v1_0_0;
CREATE SCHEMA IF NOT EXISTS dissem_copy;

CREATE SCHEMA IF NOT EXISTS api_v2_0_0;
CREATE SCHEMA IF NOT EXISTS api_v2_0_0_functions;

