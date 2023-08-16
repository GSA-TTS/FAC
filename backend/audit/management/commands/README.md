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
