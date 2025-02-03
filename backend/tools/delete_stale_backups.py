#!/usr/bin/env python
#
# Find or delete files in S3 older than a given age and matching a pattern
# Useful for cleaning up old backups, etc.
#

import boto3
from datetime import datetime, timezone, timedelta
from django.conf import settings
from optparse import OptionParser
import sys

def main(args):
    parser = OptionParser()
    parser.add_option("--delete", dest="delete", metavar="DELETE", action="store_true",
                    default=False, help="Actually do a delete. If not specified, just list the keys found that match.")
    (config, args) = parser.parse_args(args)

    config_ok = True
    for flag in ("bucket"):
        if getattr(config, flag) is None:
            print >>sys.stderr, "Missing required flag: --%s" % flag
            config_ok = False
    if not config_ok:
        print >>sys.stderr, "Configuration is not ok, aborting..."
        return 1

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_BACKUPS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_BACKUPS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_BACKUPS_ENDPOINT_URL,
    )

    objects = s3_client.list_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix="backups/")
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=1)
    # Check if the bucket contains any objects
    if 'Contents' in objects:
        for obj in objects['Contents']:
            # Get the last modified date of the object
            last_modified = obj['LastModified']

            # If the object is older than one week, delete it
            #s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f"backups/{item.file.name}")
            if config.delete:
                if last_modified < one_week_ago:
                    print(f"Deleting {obj['Key']} last modified on {last_modified}")
                    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=obj['Key'])
            else:
                print("Files: %s", s3_client.list_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=obj['Key']))
    else:
        print("No objects found in the bucket.")

if __name__ == '__main__':
  sys.exit(main(sys.argv))
