# Census to FAC data migration

## Overview

This is implemented as a Django app to leverage existing management commands and settings. It includes Python and shell scripts to:

* Load raw census data as CSV files into an S3 bucket
* Create Postgres tables from these CSV files
* Perform any data clean up required to create a table from a CSV file

## Infrastructure changes

* Create a new S3 bucket in Cloud.gov spaces as well as in the local environment
* Create a new Postgres instance both in CG and locally

## Utilities

* fac_s3.py - Uploads folders or files to an S3 bucket.

```bash
python manage.py fac_s3 fac-c2g-s3 --upload --src census_to_gsafac/data

* raw_to_pg.py - Inserts data into Postgres tables using the contents of the CSV files in the S3 bucket. The first row of each file is assumed to have the column names (we convert to lowercase). The name of the table is determined by examining the name of the file. The sample source files do not have delimters for empty fields at the end of a line - so we assume these are nulls.

```bash
python manage.py raw_to_pg --folder data
python manage.py raw_to_pg --clean True

* models.py These correspond to the incoming CSV files
* routers.py This tells django to use a different postgres instance.

* data A folder that contains sample data that we can use for development.

## Prerequisites

* A Django app that reads the tables created here as unmanaged models and populates SF-SAC tables by creating workbooks, etc. to simulate a real submission

## How to load test Census data into Postgres

1.  Download test Census data from https://drive.google.com/drive/folders/1TY-7yWsMd8DsVEXvwrEe_oWW1iR2sGoy into census_to_gsafac/data folder.  
NOTE:  Never check in the census_to_gsafac/data folder into GitHub.

2.  In the FAC/backend folder, run the following to load CSV files from census_to_gsafac/data folder into fac-c2g-s3 bucket.
```bash
python manage.py fac_s3 fac-c2g-s3 --upload --src census_to_gsafac/data
```

3.  In the FAC/backend folder, run the following to read the CSV files from fac-c2g-s3 bucket and load into Postgres.
```bash
python manage.py raw_to_pg --folder data
```