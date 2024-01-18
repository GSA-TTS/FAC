# Census to FAC data migration

## Overview

This is implemented as a Django app to leverage existing management commands and settings. It includes Python and shell scripts to:

- Load raw census data as CSV files into an S3 bucket
- Create Postgres tables from these CSV files
- Perform any data clean up required to create a table from a CSV file
- Run the historic data migrator
- Run the historic workbook generator

## Infrastructure changes

- Create a new S3 bucket in Cloud.gov spaces as well as in the local environment
- Create a new Postgres instance both in CG and locally

## Utilities

- fac_s3.py - Uploads folders or files to an S3 bucket.

```bash
python manage.py fac_s3 gsa-fac-private-s3 --upload --src census_historical_migration/data
```

- csv_to_postgres.py - Inserts data into Postgres tables using the contents of the CSV files in the S3 bucket. The first row of each file is assumed to have the column names (we convert to lowercase). The name of the table is determined by examining the name of the file. The sample source files do not have delimters for empty fields at the end of a line - so we assume these are nulls.

```bash
python manage.py csv_to_postgres --folder data --chunksize 10000
python manage.py csv_to_postgres --clean True
```

- models.py These correspond to the incoming CSV files
- routers.py This tells django to use a different postgres instance.

- data A folder that contains sample data that we can use for development.

## Prerequisites

- A Django app that reads the tables created here as unmanaged models and populates SF-SAC tables by creating workbooks, etc. to simulate a real submission

## How to load test Census data into Postgres

1.  Download test Census data from https://drive.google.com/drive/folders/1TY-7yWsMd8DsVEXvwrEe_oWW1iR2sGoy into census_historical_migration/data folder.
    NOTE: Never check in the census_historical_migration/data folder into GitHub.

2.  In the FAC/backend folder, run the following to load CSV files from census_historical_migration/data folder into gsa-fac-private-s3 bucket.

```bash
docker compose run --rm web python manage.py fac_s3 \
  gsa-fac-private-s3 \
  --upload \
  --src census_historical_migration/data
```

3.  In the FAC/backend folder, run the following to read the CSV files from gsa-fac-private-s3 bucket and load into Postgres.

```bash
docker compose run --rm web python manage.py \
  csv_to_postgres \
  --folder data \
  --chunksize 10000
```

If you find yourself loading and reloading data, you may want to truncate what is in your local DB in-between.

```
truncate table
	census_historical_migration_elecauditfindings ,
	census_historical_migration_elecauditheader ,
	census_historical_migration_elecaudits ,
	census_historical_migration_eleccaptext ,
	census_historical_migration_eleccpas ,
	census_historical_migration_eleceins ,
	census_historical_migration_elecfindingstext ,
	census_historical_migration_elecnotes ,
	census_historical_migration_elecpassthrough ,
	census_historical_migration_elecueis ,
	census_historical_migration_migrationerrordetail ,
	census_historical_migration_reportmigrationstatus
	;
```

### How to run the historic data migrator

To migrate individual dbkeys:

```
docker compose run --rm web python manage.py historic_data_migrator \
  --years 22 \
  --dbkeys 177310
```

- `year` and `dbkey` are optional. The script will use default values for these if they aren't provided.

To migrate dbkeys for a given year with pagination:

```
docker compose run --rm web python manage.py run_paginated_migration \
  --year 2022 \
  --page_size 5 \
  --pages 1,3,4
```

- `batchSize` and `pages` are optional. The script will use default values for these if they aren't provided.

### How to run the historic workbook generator:

```
docker compose run --rm web python manage.py historic_workbook_generator \
  --year 22 \
  --output <your_output_directory> \
  --dbkey 177310
```

- `year` is optional and defaults to `22`.
- The `output` directory will be created if it doesn't already exist.

### How to trigger historic data migrator from GitHub:

- Go to GitHub Actions and select `Historic data migrator` action
- Next, click on `Run workflow` on top right and
- Provide the target `environment` along with optional parameters such as `dbkeys` and `years`
- Click `Run`
