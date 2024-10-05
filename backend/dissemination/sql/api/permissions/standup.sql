-- This grants access to the tables and views that were created
-- to the API server.
GRANT SELECT ON ALL TABLES IN SCHEMA api_v1_0_3 TO api_fac_gov;
GRANT SELECT ON ALL TABLES IN SCHEMA api_v1_1_0 TO api_fac_gov;
GRANT SELECT ON ALL TABLES IN SCHEMA public_api_v1_0_0 TO api_fac_gov;
