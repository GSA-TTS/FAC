# Census to FAC data migration

## Overview

This is implemented as a Django app to leverage existing management commands and settings. It has Python and shell scripts to

* load raw census data as csv files into an S3 bucket
* create postgres tables from these csv files
* perform any data clean up required to create a table from a csv file
* perforn any ither validations or cleansing, such as verifying the integrity of df files, of data coming into FAC from Census

## Infrastructure changes

* Create a new S3 bucket in cloud.gov spaces as well as in the local environment
** Affected files: TBD
* Create a new Postgres instance both in CG and locally
** Affected files:

## Utilities

* fac_s3 - is a management command in the `support` app. It can be used to upload folders or files to an s3 bucket.

```bash
manage.py fac_s3 fac-c2g-s3 --upload --src c2g/data
```

* load_raw.py - Read zip files provided by Census, and upload them to the S3 bucket. The basename of the zip file is used to create a folder in S3. The individual unzipped files are stored in the folder. There is an assumption that there are no sub-folders.
* raw_to_pg.py - Inserts data into PG tables using the contents of the csv files in the S3 bucket. The first row of each file is assumed to have the column names (we convert to lowercase). The name of the table is determined by examining the name of the file. The sample source files do not have delimiters for empty fields at the end of a line - so we assume these are nulls.

```bash
manage.py raw_to_pg --folder data
manage.py raw_to_pg --clean True
```

* models.py These ought to correspond to the incoming csv files
* routers.py This tells django to use a different postgres instance.

* data A folder that contains sample data that we can use for development.

* wb_generator.py This module loads a single submission from the history tables to the GSA FAC tables

* loader.py This module will eventually load all of the historic data by invoking wb_generator for each submission

* c2g/workbooklib is a clone of dissemination/workbooklib

### Testing

We need to write more tests. But we have one basic test. This can be invoked as follows

```bash
manage.py test c2g
```

In addition there is a small hack in place to test with the data that was created from the Census csv files. After loading the data into minio and populating postgres as described above, we can now try to create submissions with the following command

```bash
manage.py raw_to_pg --load True 
```

Currently, the above command will stop at the first submission that fails. Note also that this program currently deletes everything in SingleAuditChecklist before it starts loading. These are things that we will address once we have most of the code working.

### Work in progress

* c2g/workbooklib has only been modified to handle general_information and federal_awards. The rest of the workbooks need to be worked on.
* Need to write more tests. Have been doing mainly manual testing so far.
* Nothing has been done yet to handle pdf files.

## Pre-requisites for

* A Django app that reads the tables created here as unmanaged models and populates SF-SAC tables by creating workbooks, etc to simulate a real submission.
