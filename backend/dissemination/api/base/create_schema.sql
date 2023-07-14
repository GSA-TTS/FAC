DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'anon') THEN
      RAISE NOTICE 'Role "anon" already exists. Skipping.';
   ELSE
      CREATE ROLE anon NOLOGIN;
   END IF;
END
$do$;

DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'authenticator') THEN
      RAISE NOTICE 'Role "authenticator" already exists. Skipping.';
   ELSE
      CREATE ROLE authenticator  LOGIN NOINHERIT NOCREATEDB NOCREATEROLE NOSUPERUSER;
   END IF;
END
$do$;

DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'api_fac_gov_anon') THEN
      RAISE NOTICE 'Role "api_fac_gov_anon" already exists. Skipping.';
   ELSE
      CREATE ROLE api_fac_gov_anon NOLOGIN;
   END IF;
END
$do$;

GRANT api_fac_gov_anon TO authenticator;

NOTIFY pgrst, 'reload schema';