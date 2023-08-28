# Loading CognizantBaseline from fixtures

If CognizantBaseline.json exists in the folder audit/fixtures, you can load it into the database using the following command:

```bash
fac loaddata audit/fixtures/CognizantBaseline.json --app audit.CognizantBaseline
```

If the fixture does not exist follow the steps below to create it.
# csv_to_pg

To use this, you need to have data in your SQLite DB.

1. Open `http://localhost:9002`
2. Log in with `minioadmin`/`minioadmin`. (This only works in the local docker stack.)
3. Create a folder called `fixture-data`.
4. In that folder, upload clean data that you created with `generate-sqlite-files`. E.g. `clean-ay19`. Upload the entire folder.

Now, run the tool:

```bash
fac csv_to_pg --path fixture-data/clean-ay19
```

(`fac` is a shorthand for... `docker compose run web manage.py ...`)

This will load the CSVs from the files in the S3 bucket into the PG database. This approach is being used because we can also replicate it in our dev, staging, and preview environments.
# make_cog_baseline

Once census_gen19 and census_cfda19 tables have been populated, run the program to calculate and populate CognizantBaseline table.
The command for this is:

```bash
fac make_cog_baseline
```
Now create a fixture for this table as follows:

```bash
fac dumpdata audit.CognizantBaseline --output audit/fixtures/CognizantBaseline.json
```

Make sure that the fixture file is tracked in git

# make_cog_over_for_2022

Make sure CognizantBaseline.json is available in audit/fixtures.  If not, follow the steps above to create it.

Load data from CognizantBaseline.json following procedure above.

Populate census_gen22 and census_cfda22 tables similar to the census_gen19 and census_cfda19 tables above.

Test cog / over with 2022 data, run the following:
```bash
fac make_cog_over_for_2022
```