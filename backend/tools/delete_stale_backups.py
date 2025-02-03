#!/usr/bin/env python
#
# Find or delete files in S3 older than a given age and matching a pattern
# Useful for cleaning up old backups, etc.
#
# References:
# https://stackoverflow.com/questions/11426560/amazon-s3-boto-how-to-delete-folder
# https://github.com/jordansissel/s3cleaner/blob/master/s3cleaner.py
#

import boto3
import json
import environs
from datetime import datetime, timezone, timedelta
from django.conf import settings
from optparse import OptionParser
import sys

env = environs.Env()

def main(args):
    parser = OptionParser()
    parser.add_option("--days", dest="days", metavar="DAYS", type="int",
                    help="Max age a key(file) in days can have before we want to delete it")
    parser.add_option("--delete", dest="delete", metavar="DELETE", action="store_true",
                    default=False, help="Actually do a delete. If not specified, just list the keys found that match.")
    (config, args) = parser.parse_args(args)

    # config_ok = True
    # for flag in ("days"):
    #     if getattr(config, flag) is None:
    #         print >>sys.stderr, "Missing required flag: --%s" % flag
    #         config_ok = False
    # if not config_ok:
    #     print >>sys.stderr, "Configuration is not ok, aborting..."
    #     return 1

    vcap = json.loads(env.str("VCAP_SERVICES"))
    for service in vcap["s3"]:
        if service["instance_name"] == "backups":
            # Backups AWS S3 bucket for the app's backup files
            s3_creds = service["credentials"]

            AWS_BACKUPS_ACCESS_KEY_ID = s3_creds["access_key_id"]
            AWS_BACKUPS_SECRET_ACCESS_KEY = s3_creds["secret_access_key"]
            AWS_BACKUPS_STORAGE_BUCKET_NAME = s3_creds["bucket"]

            AWS_S3_BACKUPS_REGION_NAME = s3_creds["region"]
            AWS_S3_BACKUPS_CUSTOM_DOMAIN = f"{AWS_BACKUPS_STORAGE_BUCKET_NAME}.s3-{AWS_S3_BACKUPS_REGION_NAME}.amazonaws.com"
            AWS_S3_BACKUPS_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

            AWS_S3_BACKUPS_ENDPOINT = s3_creds["endpoint"]
            AWS_S3_BACKUPS_ENDPOINT_URL = f"https://{AWS_S3_BACKUPS_ENDPOINT}"

            # in deployed environments, the internal & external endpoint URLs are the same
            AWS_S3_BACKUPS_INTERNAL_ENDPOINT = AWS_S3_BACKUPS_ENDPOINT_URL
            AWS_S3_BACKUPS_EXTERNAL_ENDPOINT = AWS_S3_BACKUPS_ENDPOINT_URL


    #settings.configure()
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_BACKUPS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_BACKUPS_SECRET_ACCESS_KEY,
        endpoint_url=AWS_S3_BACKUPS_ENDPOINT_URL,
    )
    # s3_client = boto3.client(
    #     "s3",
    #     aws_access_key_id=settings.AWS_BACKUPS_ACCESS_KEY_ID,
    #     aws_secret_access_key=settings.AWS_BACKUPS_SECRET_ACCESS_KEY,
    #     endpoint_url=settings.AWS_S3_BACKUPS_ENDPOINT_URL,
    # )

    objects = s3_client.list_objects(Bucket=AWS_BACKUPS_STORAGE_BUCKET_NAME, Prefix="backups/")
    #objects = s3_client.list_objects(Bucket=settings.AWS_BACKUPS_STORAGE_BUCKET_NAME, Prefix="backups/")
    delete_older_than = datetime.now(timezone.utc) - timedelta(days=config.days)
    # Check if the bucket contains any objects
    if 'Contents' in objects:
        for obj in objects['Contents']:
            # Get the last modified date of the object
            last_modified = obj['LastModified']

            # If the object is older than one week, delete it
            #s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f"backups/{item.file.name}")
            if config.delete:
                if last_modified < delete_older_than:
                    print(f"Deleting {obj['Key']} last modified on {last_modified}")
                    s3_client.delete_object(Bucket=AWS_BACKUPS_STORAGE_BUCKET_NAME, Key=obj['Key'])
                    #s3_client.delete_object(Bucket=settings.AWS_BACKUPS_STORAGE_BUCKET_NAME, Key=obj['Key'])
                else:
                    print(f"Object {obj['Key']} younger than {delete_older_than} days. Not deleting.")
            else:
                print(f"Delete not sent. {obj['Key']} was last modified on {last_modified}")
    else:
        print("No objects found in the bucket.")

if __name__ == '__main__':
  sys.exit(main(sys.argv))
