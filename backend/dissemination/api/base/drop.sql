-- Query cannot be empty.
DROP ROLE IF EXISTS authenticator;
DROP ROLE IF EXISTS anon;
DROP ROLE IF EXISTS api_fac_gov_anon;

NOTIFY pgrst, 'reload schema';