#####################
# HOW TO USE
# This management command is intended to export our currently live
# data to a set of CSV files.
#
# It exports data in both as audit-years and fiscal-years.
# This means we get one set of data that is based on the
# `audit_year` column in `general`, and the other set
# is based on {year-1}-10-01 to {year}-09-30.
#
# We end up with a directory structure in S3 that looks like this:
#
# audit-year/
#   fac-2016-ay.zip
#   fac-2017-ay.zip
#   ...
# fiscal-year/
#   fac-2016-ffy.zip
#   fac-2017-ffy.zip
#   ...
#
# We can put that in any bucket and root we want. A production usage might
# look like:
#
# python manage.py export_data_to_s3 --bucket fac-private-s3 --path public-data/gsa
#
# and a local usage might look like
#
# fac export_data_to_s3 --bucket gsa-fac-private-s3 --path test

import logging
import boto3
from boto3.s3.transfer import TransferConfig
from botocore.client import Config
from sys import exit
from os import makedirs
from pathlib import Path
import shutil
import pandas as pd
from collections import namedtuple as NT
from datetime import datetime
from sqlalchemy import create_engine
import time
from config.vcap import GET, FIND, get_vcap_services
import os
import sys
import zipfile

from django.core.management.base import BaseCommand
from django.conf import settings

# from config import settings


logger = logging.getLogger(__name__)

Table = NT("Table", "name is_suppressed source")

API_VERSION = "api_v1_1_0"
CURRENT_YEAR = datetime.now().year
NEXT_YEAR = datetime.now().year + 1
FLAGS_INVALID = True
FLAGS_VALID = False
SOURCE_API = 0
SOURCE_INTERNAL = 1

TABLES = [
    Table("general", False, SOURCE_API),
    Table("federal_awards", False, SOURCE_API),
    Table("findings", False, SOURCE_API),
    Table("findings_text", True, SOURCE_API),
    Table("corrective_action_plans", True, SOURCE_API),
    Table("passthrough", False, SOURCE_API),
    Table("notes_to_sefa", True, SOURCE_API),
    Table("additional_eins", False, SOURCE_API),
    Table("additional_ueis", False, SOURCE_API),
    Table("secondary_auditors", False, SOURCE_API),
]

MIGRATION_TABLES = [
    Table("migrationinspectionrecord", True, SOURCE_INTERNAL),
    Table("invalidauditrecord", True, SOURCE_INTERNAL),
]


# get_s3_client :: string -> s3 client, creds dict, bool
# Depending on the environment we are in, we either
# get the local minio creds (defined in settings/docker container)
# or we reach into the VCAP_SERVICES env var to get the credentials we need.
def get_s3_client(bucket):
    in_cloud = False
    if os.getenv("ENV") in ["SANDBOX", "PREVIEW", "DEV", "STAGING", "PRODUCTION"]:
        in_cloud = True
    if in_cloud:
        creds = get_vcap_services([GET("s3"), FIND("name", bucket), GET("credentials")])
        # We have to unset the proxy for S3 operations.
        os.environ["https_proxy"] = ""
    else:
        creds = {
            "region": settings.AWS_S3_PRIVATE_REGION_NAME,
            "access_key_id": settings.AWS_PRIVATE_ACCESS_KEY_ID,
            "secret_access_key": settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
            "endpoint": settings.AWS_S3_PRIVATE_ENDPOINT,
        }

    creds["bucket"] = bucket
    creds["in_cloud"] = in_cloud

    # Define the endpoint for containerized testing.
    client = boto3.client(
        service_name="s3",
        region_name=creds["region"],
        aws_access_key_id=creds["access_key_id"],
        aws_secret_access_key=creds["secret_access_key"],
        endpoint_url=None if in_cloud else creds["endpoint"],
        config=Config(signature_version="s3v4"),
    )
    return client, creds, in_cloud


# get_conn_string
# If we are in a cloud environment, it gets the brokered connection information for
# the Postgres instance; if we are running locally, values are hard-coded against our
# containerized stack.
def get_conn_string():
    if os.getenv("ENV") in ["SANDBOX", "PREVIEW", "DEV", "STAGING", "PRODUCTION"]:
        creds = get_vcap_services(
            [GET("aws-rds"), FIND("name", "fac-db"), GET("credentials")]
        )
        conn_string = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
            creds["username"],
            creds["password"],
            creds["host"],
            creds["port"],
            creds["db_name"],
        )
    else:  # LOCAL or TESTING
        conn_string = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
            "postgres",
            "",
            "db",
            5432,
            "postgres",
        )
    return conn_string


# get_sqlalchemy_engine
# This is a thin wrapper that gets a correct connection string
# and builds an engine. We are using SQLAlchemy becuase Pandas
# prefers it, and we want the chuncked data access that Pandas provides
# for creating CSV files from SQL.
def get_sqlalchemy_engine():
    connection_string = get_conn_string()
    engine = create_engine(connection_string)
    return engine


# destination_key
# Mangles strings so that they come out as clean
# destination keys for S3.
def destination_key(key, file):
    if key.endswith("/"):
        return key + file
    else:
        return key + "/" + file


# uploadFileS3 :: string string string
# Takes a bucket, destination key, and local filename
# and uploads that file to S3.
def uploadFileS3(bucket, key, file):
    client, creds, _ = get_s3_client(bucket)
    config = TransferConfig(
        multipart_threshold=1024 * 25,
        max_concurrency=10,
        multipart_chunksize=1024 * 25,
        use_threads=True,
    )
    client.upload_file(
        file,
        creds["bucket"],
        destination_key(key, file),
        Config=config,
    )
    client.close()


# run_query :: string, string, int
# Runs an SQL query, generating a CSV file to the filepath.
# Runs the SQL in chunksize rows per query, using Pandas.
# This lets us keep the memory low on both the client and
# the server. Recommended around 10K-20K rows.
def run_query(FILEPATH, query, chunksize):
    engine = get_sqlalchemy_engine()
    header = True
    logger.info(query)
    for df in pd.read_sql(query, engine, chunksize=chunksize):
        df.to_csv(FILEPATH, mode="a", header=header, index=False)
        # Only drop the header on the first chunk.
        header = False


# exit_with_message :: string, exception
# A helper to log an error, log the exception, and
# then system exit. This way, failures are clearly caught
# in the job run via GH Action.
def exit_with_message(msg, e):
    logger.error(msg)
    logger.error(e)
    sys.exit(-1)


# dump_api_table :: string, string, int, string, int
# Given a directory, it dumps a table to that directory.
# The year_type is either "ay" for audit_year, or "ffy" for
# Federal fiscal year. It chunks in `chunksize` rows per query.
def dump_api_table(dir, table, year, year_type, chunksize):
    # Always try and make the destination directory
    # The param exists_ok will prevent errors
    FILEPATH = Path(dir) / f"{table.name}.csv"
    if year_type == "ay":
        where_clause = " ".join(
            [
                "WHERE report_id IN",
                f"(select report_id from {API_VERSION}.general",
                f"WHERE audit_year = '{year}'",
                f"AND is_public=true" if table.is_suppressed else "",
                ")",
            ]
        )
    elif year_type == "ffy":
        where_clause = " ".join(
            [
                "WHERE report_id IN",
                f"(select report_id from {API_VERSION}.general",
                f"WHERE fac_accepted_date >= '{year-1}-10-01'::DATE",
                f"AND fac_accepted_date <= '{year}-09-30'::DATE",
                f"AND is_public=true " if table.is_suppressed else "",
                ")",
            ]
        )
    query = " ".join([f"SELECT * from {API_VERSION}.{table.name} ", where_clause])
    run_query(FILEPATH, query, chunksize)


# dump_full_api_table :: string string string int
# Uses the views defined in the API to access data. Dumps full
# tables (e.g. all of general) to a CSV, zips that CSV, and uploads it.
# The files are always cleaned up.
# This only needs to run once; it is all data, not yearly.
def dump_full_api_table(bucket, key, table, chunksize):
    # Always try and make the destination directory
    # The param exists_ok will prevent errors
    FILEPATH = f"{table.name}.csv"
    if table.is_suppressed:
        where_clause = " ".join(
            [
                "WHERE report_id IN",
                f"(select report_id from {API_VERSION}.general WHERE is_public=true)",
            ]
        )
    else:
        where_clause = ""
    query = " ".join([f"SELECT * from {API_VERSION}.{table.name}", where_clause])
    run_query(FILEPATH, query, chunksize)
    # shutil.make_archive(table.name, "zip", FILEPATH)
    try:
        zipf = zipfile.ZipFile(f"{table.name}.zip", "w", zipfile.ZIP_DEFLATED)
        zipf.write(f"{table.name}.csv")
        zipf.close()
    except Exception as e:
        exit_with_message("could not create zip of csv", e)
    try:
        uploadFileS3(bucket, destination_key(key, "full/"), f"{table.name}.zip")
    except Exception as e:
        exit_with_message("failed to upload to S3", e)
    # Remove the zipfile
    Path(f"{table.name}.zip").unlink(missing_ok=True)
    Path(f"{table.name}.csv").unlink(missing_ok=True)


# dump_internal_table :: string string int string int
# Dumps a table by audit year or federal fiscal year.
# Chunks it, and puts it in a directory as a CSV.
# We later zip the whole directory for upload, not here.
def dump_internal_table(dir, table, year, year_type, chunksize):
    if year_type == "ay":
        FILEPATH = Path(dir) / f"{table.name}.csv"
        where_clause = " ".join(
            [
                "WHERE report_id IN",
                f"(select report_id from {API_VERSION}.general",
                f"WHERE audit_year = '{year}'",
                f"AND is_public=true" if table.is_suppressed else "",
                ")",
            ]
        )
        query = " ".join(
            [f"SELECT * from public.dissemination_{table.name}", where_clause]
        )
        run_query(FILEPATH, query, chunksize)


# sling_tables :: string array string int array int bool?
# For all given audit year types, and all years, it goes through and dumps
# tables to a folder auto-named for the year and audit year type.
# That folder of all (by-year) tables is then zipped and uploaded.
# Slightly different logic for the API tables vs. the migration/inspection
# tables, but otherwise are handled very similarly.
def sling_tables(bucket, tables, key, year, year_types, chunksize, run_full=False):

    # Given a year type ("`ay" or "fy")
    # I want to dump all the tables and compress them.
    # We'll put them at a path based on the year
    for year_type in year_types:
        if year_type == "ffy":
            dest_key = destination_key(key, "fiscal-year/")
        elif year_type == "ay":
            dest_key = destination_key(key, "audit-year/")
        elif year_type == "migration":
            dest_key = destination_key(key, "migration/")

        DIRECTORY = f"fac-{year}-{year_type}"
        makedirs(DIRECTORY, exist_ok=True)

        # A .zip will be added automatically
        ZIPNAME = DIRECTORY

        # This will create one directory per year
        # where each directory contains all the tables\
        for table in tables:
            if table.source == SOURCE_API:
                try:
                    dump_api_table(DIRECTORY, table, year, year_type, chunksize)
                except Exception as e:
                    exit_with_message("failed to dump and upload API tables", e)
            elif table.source == SOURCE_INTERNAL and year < 2023:
                # Migration tables only exist before 2023.
                try:
                    dump_internal_table(DIRECTORY, table, year, year_type, chunksize)
                except Exception as e:
                    exit_with_message(
                        "failed to dump and upload internal/migration tables", e
                    )
        # Now, compress that directory
        shutil.make_archive(ZIPNAME, "zip", DIRECTORY)
        # Remove the original directory
        # Copy things to S3
        try:
            uploadFileS3(bucket, dest_key, f"{ZIPNAME}.zip")
        except Exception as e:
            exit_with_message("failed to upload to S3", e)

        # Always cleanup, even if we threw an exception
        shutil.rmtree(DIRECTORY)
        # Remove the zipfile
        Path(f"{ZIPNAME}.zip").unlink(missing_ok=True)


# invalid_flags :: flags
# Makes sure all flags passed to the script are valid
def invalid_flags(flags):
    # Flags is a string
    if flags["year"] in "ALL":
        pass
    elif int(flags["year"]) < 2016:
        logger.error(f"{flags['year']} must be greater or equal to 2015.")
        return FLAGS_INVALID
    elif int(flags["year"]) > 2200:
        logger.error(f"{flags['year']} must be less than 2200.")
        return FLAGS_INVALID

    if not flags["use_ay"] and not flags["use_ffy"] and not flags["use_ay_and_ffy"]:
        logger.error(
            "one of --audit-year, --fiscal-year, or --all-year-types must be present"
        )
        return FLAGS_INVALID

    return FLAGS_VALID


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Source flags
        parser.add_argument("--year", type=str, default="ALL")

        # What date range?
        parser.add_argument("--audit-year", dest="use_ay", action="store_true")
        parser.add_argument("--fiscal-year", dest="use_ffy", action="store_true")
        parser.add_argument(
            "--all-year-types", dest="use_ay_and_ffy", action="store_true", default=True
        )

        # Destination flags
        parser.add_argument("--bucket", type=str, required=True)
        parser.add_argument("--path", type=str, required=True)

        parser.add_argument("--chunksize", type=int, required=False, default=10_000)
        pass

    def handle(self, *args, **flags):
        # Validate all of the flags; if they are
        # invalid, exit.
        if invalid_flags(flags):
            exit_with_message("invalid command-line flags", flags)

        # Turn the singletons into lists.
        # Even if we're only doing one year, make it a
        # list so we can loop over it.
        if flags["year"] in "ALL":
            years = range(2016, NEXT_YEAR)
        else:
            years = [int(flags["year"])]

        if flags["use_ay_and_ffy"]:
            year_types = ["ay", "ffy"]
        else:
            year_types = []
            if flags["use_ay"]:
                year_types.append("ay")
            if flags["use_ffy"]:
                year_types.append("ffy")

        start = time.time()

        # Run the dump of the full tables.
        for table in TABLES:
            dump_full_api_table(
                flags["bucket"], flags["path"], table, chunksize=flags["chunksize"]
            )

        # Run the yearly tables
        for year in reversed(years):
            sling_tables(
                flags["bucket"],
                TABLES,
                flags["path"],
                year=year,
                year_types=year_types,
                chunksize=flags["chunksize"],
            )
            sling_tables(
                flags["bucket"],
                MIGRATION_TABLES,
                flags["path"],
                year=year,
                year_types=["migration"],
                chunksize=flags["chunksize"],
            )
        logger.info(f"CSV dump elapsed time: {time.time() - start}s")
