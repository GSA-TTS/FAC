from os import path
import os

import boto3

from django.core.management.base import BaseCommand

from django.conf import settings


class Command(BaseCommand):
    help = """
    Alternative to aws s3 as the cli is not available in production.
    Usage:
        manage.py fac_s3 <bucket_name> --cp --src SRC [--tgt TGT]
        manage.py fac_s3 <bucket_name> --ls [--tgt TGT]
    """

    def add_arguments(self, parser):
        parser.add_argument("bucket_name", type=str, help="The S3 bucket name.")
        parser.add_argument("--src", help="local file name.")
        parser.add_argument("--tgt", help="s3 file name.")
        parser.add_argument("--ls", action="store_true", help="List all files.")
        parser.add_argument("--cp", action="store_true", help="Copy src to tgt.")
        parser.add_argument("--rm", action="store_true", help="Delete tgt.")

    def handle(self, *args, **options):
        bucket_name = options["bucket_name"]
        src_path = options["src"]
        tgt_path = options["tgt"]

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )

        if options["ls"]:
            items = s3_client.list_objects(
                Bucket=bucket_name,
                Prefix=tgt_path or "",
            )["Contents"]
            for item in items:
                print(item["Key"], item["Size"], item["LastModified"])
            return

        if options["cp"]:
            file_path = path.join(settings.BASE_DIR, src_path)
            # with open(file_path, 'rb') as file:
            object_name = tgt_path or os.path.basename(file_path)
            s3_client.upload_file(file_path, bucket_name, object_name)
            print(f"Copied {file_path} to {bucket_name} {object_name}.")
            return

        if options["rm"]:
            s3_client.delete_object(
                Bucket=bucket_name,
                Key=tgt_path,
            )
