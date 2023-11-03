# Census to FAC data migration

## Overview

This is implemented as a django app to leverage existing management commands and settings. It has python and shell scripts to

* load raw census data as csv files into an S3 bucket
* create postgres tables from these csv files
* perform any data clean up required to create a table from a csv file
* perforn any ither validations or cleansing, such as verifying the integrity of df files, of data coming into FAC from Census

## Infrastructure changes

* Create a new S3 bucket in cloud.gov spaces as well as in the local environment
* Create a new Postgres instance both in CG and locally

## Utilities

* fac_s3.py - Uploads folders or files to an s3 nucket.

```bash
manage.py fac_s3 fac-c2g-s3 --upload --src census_to_gsafac/data
```

* raw_to_pg.py - Inserts data into PG tables using the contents of the csv files in the S3 bucket. The first row of each file is assumed to have the column names (we convert to lowercase). The name of the table is determined by examining the name of the file. The sample source files do not have delimters for empty fields at the end of a line - so we assume these are nulls.

```bash
manage.py raw_to_pg --folder data
manage.py raw_to_pg --clean True
```

* models.py These ought to correspons to the incoming csv files
* routers.py This tells django to use a different postgres instance.

* data A folder that contains sample data that we can use for development.

## Pre-requisites for

* A django app that reads the tables created here as unmanaged models and populates SF-SAC tables by creating workbooks, etc to simulate a real submission

## How to load test Census data into postgres?

1.  Download test Census data from https://drive.google.com/drive/folders/1TY-7yWsMd8DsVEXvwrEe_oWW1iR2sGoy into census_to_gsafac/data folder.

2.  In the FAC/backend folder, run the following to load csv files from census_to_gsafac/data folder into fac-c2g-s3 bucket.
```bash
python manage.py fac_s3 fac-c2g-s3 --upload --src census_to_gsafac/data
```

3.  In the FAC/backend folder, run the following to read the csv files from fac-c2g-s3 bucket and load into postgres.
```bash
manage.py raw_to_pg --folder data
```