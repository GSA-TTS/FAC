# API versions

When adding a new API version.

1. Create a folder in api/dissemination for the version name. E.g. `v1_0_1`. 
2. Create `db_views.sql` and `init_api_db.sql`. Make sure the schema used throughout is your new version number.
3. Update `.profile` in `backend`. The variable `API_VERSIONS` should be a comma-separated list of version numbers.
4. Update `docker-compose.yml` and `docker-compose-web.yml` to change the `PGRST_DB_SCHEMAS` key to reflect all the active schemas. 
   1. ADD TO THE END OF THIS LIST. The first entry is the default. Only add to the front of the list if we are certain the schema should become the new default.
   2. This is likely true of TESTED patch version bumps (v1_0_0 to v1_0_1), and *maybe* minor version bumps (v1_0_0 to v1_1_0). MAJOR bumps require change management messaging.
 