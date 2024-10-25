-- This grants access to the tables and views that were created
-- to the API server.

-- Decommissioned 20241024
-- GRANT SELECT ON ALL TABLES IN SCHEMA api_v1_0_3 TO api_fac_gov;
GRANT SELECT ON ALL TABLES IN SCHEMA api_v1_1_0 TO api_fac_gov;
GRANT SELECT ON ALL TABLES IN SCHEMA api_v2_0_0 TO api_fac_gov;

-- GRANT SELECT ON SEQUENCES IN SCHEMA public_data_v1_0_0;
-- -- SEQ: USAGE | SELECT | UPDATE
-- ALTER DEFAULT PRIVILEGES
--     IN SCHEMA public_data_v1_0_0 
--     GRANT SELECT, USAGE 
--     ON SEQUENCES 
--     TO api_fac_gov;
