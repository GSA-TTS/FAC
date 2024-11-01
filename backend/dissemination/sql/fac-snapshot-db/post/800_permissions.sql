-- This grants access to the tables and views that were created
-- to the API server.

-- Decommissioned 20241024
-- GRANT SELECT ON ALL TABLES IN SCHEMA api_v1_0_3 TO api_fac_gov;

-----------------------------------------------------
-- api_v1_1_0 PERMISSIONS
-----------------------------------------------------
GRANT USAGE ON SCHEMA api_v1_1_0_functions TO api_fac_gov;
GRANT USAGE ON SCHEMA api_v1_1_0 TO api_fac_gov;
GRANT SELECT ON ALL TABLES IN SCHEMA api_v1_1_0 TO api_fac_gov;
-- GRANT SELECT ON ALL TABLES IN SCHEMA dissem_copy to api_fac_gov;

-- There are no sequences currently on api_v1_1_0
-- GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA api_v1_1_0 TO api_fac_gov;

-----------------------------------------------------
-- api_v2_0_0 PERMISSIONS
-----------------------------------------------------
GRANT USAGE ON SCHEMA api_v2_0_0_functions TO api_fac_gov;
GRANT USAGE ON SCHEMA api_v2_0_0 TO api_fac_gov;
GRANT SELECT ON ALL TABLES IN SCHEMA api_v2_0_0 TO api_fac_gov;
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA api_v2_0_0 TO api_fac_gov;
