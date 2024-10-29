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
DROP SCHEMA IF EXISTS public_data_v1_0_0 CASCADE;
DROP SCHEMA IF EXISTS public_data_v1_0_0_functions CASCADE;
DROP SCHEMA IF EXISTS suppressed_data_v1_0_0 CASCADE;
DROP SCHEMA IF EXISTS suppressed_data_v1_0_0_functions CASCADE;

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
CREATE SCHEMA IF NOT EXISTS suppressed_data_v1_0_0_functions;
CREATE SCHEMA IF NOT EXISTS dissem_copy;

CREATE SCHEMA IF NOT EXISTS api_v2_0_0;
CREATE SCHEMA IF NOT EXISTS api_v2_0_0_functions;

