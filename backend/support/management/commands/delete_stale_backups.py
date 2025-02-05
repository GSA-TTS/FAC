# Usage:
# Do a delete: python manage.py delete_stale_backups --days X --delete true
# List objects: python manage.py delete_stale_backups --days X

import boto3
from datetime import datetime, timezone, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
import sys


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            required=True,
            help="Max age a key(file) in days can have before we want to delete it. Value must be (14) or greater.",
        )
        parser.add_argument(
            "--delete",
            required=False,
            default=False,
            help="True/False. Actually do a delete. If not specified, just list the keys found that match.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        delete = options["delete"]

        if days < 14:
            print(
                "Days cannot less than 14 to prevent up-to-date backups from being deleted. Exiting..."
            )
            sys.exit(1)

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_BACKUPS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_BACKUPS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_BACKUPS_ENDPOINT_URL,
        )

        objects = s3_client.list_objects(
            Bucket=settings.AWS_BACKUPS_STORAGE_BUCKET_NAME, Prefix="backups/"
        )
        delete_older_than = datetime.now(timezone.utc) - timedelta(days=days)
        # Check if the bucket contains any objects
        if "Contents" in objects:
            for obj in objects["Contents"]:
                # Get the last modified date of the object
                last_modified = obj["LastModified"]

                # If the object is older than one week, delete it
                # s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f"backups/{item.file.name}")
                if delete:
                    if last_modified < delete_older_than:
                        print(f"Deleting {obj['Key']} last modified on {last_modified}")
                        s3_client.delete_object(
                            Bucket=settings.AWS_BACKUPS_STORAGE_BUCKET_NAME,
                            Key=obj["Key"],
                        )
                    else:
                        print(
                            f"Object {obj['Key']} younger than {delete_older_than}. Not deleting."
                        )
                else:
                    print(
                        f"Delete not sent. {obj['Key']} was last modified on {last_modified}"
                    )
        else:
            print("No objects found in the bucket.")
