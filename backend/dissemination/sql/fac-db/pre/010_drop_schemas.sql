-- On fac-db, we can drop all the schemas that we're no longer
-- serving off of this database.
-- It is a kind of "spring cleaning," and it is OK if it continues to
-- run for the forseeable future.
DROP SCHEMA IF EXISTS api_v1_0_3 CASCADE;
DROP SCHEMA IF EXISTS api_v1_1_0 CASCADE;
DROP SCHEMA IF EXISTS api_v1_1_1 CASCADE;
DROP SCHEMA IF EXISTS admin_api_v1_1_0 CASCADE;
DROP SCHEMA IF EXISTS admin_api_v1_1_1 CASCADE;
