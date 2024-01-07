# Sample run

```
mkdir ${PWD}/RAMDISK
sudo mount -t tmpfs -o size=128m RAMDISK ${PWD}/RAMDISK
source configure_environment.bash
python renaming.py setup run.db
python renaming.py load run.db ims.json audit.json
python renaming.py prep run.db
python renaming.py check run.db --year 2021 --limit 100
python renaming.py copy run.db --year 2021
sudo umount ${PWD}/RAMDISK
```
# Preparing to run

To start, you need to have some environment variables set up.

For testing, we will work against the preview environment. We 
will be copying data into the preview environment from the production
bucket where Census is sending data.

You need the following. The naming matters for these scripts. 
You might change the KEY_NAME variable.

```
cf target -s preview

PREVIEW_SERVICE_INSTANCE_NAME=fac-private-s3
PREVIEW_KEY_NAME=jadud-fac-private-s3

cf create-service-key "${PREVIEW_SERVICE_INSTANCE_NAME}" "${PREVIEW_KEY_NAME}"
PREVIEW_S3_CREDENTIALS=$(cf service-key "${PREVIEW_SERVICE_INSTANCE_NAME}" "${PREVIEW_KEY_NAME}" | tail -n +2)

export PREVIEW_AWS_ACCESS_KEY_ID=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.access_key_id')
export PREVIEW_AWS_SECRET_ACCESS_KEY=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.secret_access_key')
export PREVIEW_BUCKET_NAME=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.bucket')
export PREVIEW_URI=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.uri')
export PREVIEW_AWS_DEFAULT_REGION=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.region')
```

Now, you also need to grab the bucket where the Census data lives. 
This is *dangerous*. We don't want to damage that data.

```
# The bucket is in the production environment.
# We have to switch there to grab the credentials.
cf target -s production

CENSUS_SERVICE_INSTANCE_NAME=Census-data-transfer
CENSUS_KEY_NAME=jadud-s3-key

cf create-service-key "${CENSUS_SERVICE_INSTANCE_NAME}" "${CENSUS_KEY_NAME}"
CENSUS_S3_CREDENTIALS=$(cf service-key "${CENSUS_SERVICE_INSTANCE_NAME}" "${CENSUS_KEY_NAME}" | tail -n +2)

export CENSUS_AWS_ACCESS_KEY_ID=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.access_key_id')
export CENSUS_AWS_SECRET_ACCESS_KEY=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.secret_access_key')
export CENSUS_BUCKET_NAME=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.bucket')
export CENSUS_URI=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.uri')
export CENSUS_AWS_DEFAULT_REGION=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.region')

# Don't leave us in the production environment.
cf target -s preview
```

This is all in `configure_environment.bash`, and can/should be sourced in 

```
source configure_environment.bash
```

Now, we'll have a bunch of environment variables set up.

## Setup for running

```
python renaming.py setup renaming_tracker.sqlite3
```

This creates an SQLite DB called `renaming_tracker.sqlite3`.

Indicies are created on `audityear` and `dbkey` in the `Audit` model, as these are used in the renaming process (and involve expensive lookups otherwise).

## Load needed data

You'll need JSON dumps of both `ELECAUDITHEADER_IMS` and `ELECAUDITHEADER`, one in each of two files.

These tables are all public data. (That is, suppressed data for tribal audits is not in these tables.)

Using DBeaver, dump these tables to JSON, with no breaks, so that all of the data from each table is in its own, single file.

```
> python renaming.py load --help
Usage: renaming.py load [OPTIONS] DB_FILENAME IMS_FILENAME AUDIT_FILENAME

> python renaming.py load renaming_tracker.sqlite3 ims.json audit.json
```

This will take a bit. It loads all of the data from the JSON files into the Sqlite database. This information is used for grabbing the filenames in the Census bucket, and constructing new-style GSA names for copying into a destination bucket.

## Renaming prep

The next step is to prepare for renaming all of the files. 

This does **NOT** alter any files in S3. It walks the DB tables and sets up all of the names
in the `renaming` table. This table is then used for tracking the renaming process.

```
python renaming.py prep renaming_tracker.sqlite3
```

This will also take a while. When it is done, it will have populated the `gsa_name` column in the database with the appropriate target filename for all of the files involved.

## Checking

Now, we want to check if the source files exist.

```
$ python renaming.py check --help
Usage: renaming.py check [OPTIONS]

Options:
  -l, --limit TEXT
  -y, --year INTEGER
  --help              Show this message and exit.
```

To test things, set a `--limit`.

```
python renaming.py check renaming_tracker.sqlite3 --limit 10 --year 2022
```

And, to run a particular year, enter the full year. A year takes around 1.5h to run.

The year is actually being used to run a `startswith()` query on the `gsa_name` field.

This code *does* interact with the Census bucket. It does `s3.head_object` operations to determine if files exist. If a `200` comes back, we record (in the local Sqlite3 database) that the file exists; if a `404` or other error comes back (in which case, `boto3` throws an exception), we record that file as *not existing*. There are currently no retries.

When we are done, all of the entries for a given year will have the `census_file_exists` column populated with a True/False value (0 or 1 in Sqlite). 

This is pretty slow. I haven't worked to figure out how to speed it up. Probably *mumble mumble transactions mumble* or something.

## Note: These are sharable

At this point, if you run all of the checks, it is possible to save/store this file. The Sqlite file contains no withheld tribal data, and it contains a complete track of our renaming operations.

We can use this for communicating with Census about what is present/what is missing.

## Doing the renaming

Having ascertained that 

1. We have correctly constructed paths to Census files
2. Files do or do not exist


we can now run the renaming process.

## Mangling the data

The actual data is awful.

Using 

ELECAUDITHEADER

and 

ELECAUDITHEADER_IMS

I first

perl -i -pe 's/\}/\)/g' *.csv

the two files, to convert the one } in the file to a ) (which is should be)

then I 

perl -i -pe 's/\|\|/\}/g' *.csv

to convert all || into a }, which gives me a single-character separator.

I then

vd --csv-delimiter "}" ELECAUDITHEADER.csv

to use visidata to delete the last four (null) columns of that file. They break SQLite.

then

vd --csv-delimiter "}" ELECAUDITHEADER.csv -b -o full.db

to convert the file to SQLite.

Then I load it

sqlite3 full.db

> .mode csv
> .separator }
> .import ELECAUDITHEADER_IMS.csv ELECAUDITHEADER_IMS

This gives me a DB ready for use.

I then manually create the indexes in ELECAUDITHEADER, so that things go faster.

CREATE INDEX idx_audityear ON ELECAUDITHEADER(AUDITYEAR);
CREATE INDEX idx_dbkey ON ELECAUDITHEADER(DBKEY);
CREATE INDEX idx_ay_dbkey ON ELECAUDITHEADER(AUDITYEAR, DBKEY);

