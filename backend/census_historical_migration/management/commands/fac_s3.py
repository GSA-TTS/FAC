from os import path
import os

import boto3

from django.core.management.base import BaseCommand

from django.conf import settings


class Command(BaseCommand):
    help = """
    Alternative to aws s3 as the cli is not available in production.
    Usage:
        manage.py fac_s3 <bucket_name> --upload --src SRC [--tgt TGT]
        manage.py fac_s3 <bucket_name> --download --src SRC [--tgt TGT]
        manage.py fac_s3 <bucket_name> --rm --tgt TGT]
        manage.py fac_s3 <bucket_name> --ls [--tgt TGT]
    """

    def add_arguments(self, parser):
        parser.add_argument("bucket_name", type=str, help="The S3 bucket name.")
        parser.add_argument("--src", help="local file name.")
        parser.add_argument("--tgt", help="s3 file name.")
        parser.add_argument("--ls", action="store_true", help="List all files.")
        parser.add_argument(
            "--upload", action="store_true", help="Copy local src to S3 tgt."
        )
        parser.add_argument(
            "--download", action="store_true", help="Copy S3 tgt to local src."
        )
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
            ).get("Contents")
            if not items:
                print("Target is empty")
                return
            for item in items:
                print(item["Key"], item["Size"], item["LastModified"])
            return

        if options["upload"]:
            file_path = path.join(settings.BASE_DIR, src_path)
            tgt_name = tgt_path or os.path.basename(file_path)
            tgt_name_offset = len(str(file_path))
            for subdir, dir, files in os.walk(file_path):
                object_name = tgt_name + str(subdir)[tgt_name_offset:] + "/"
                print(subdir, dir, object_name, files)
                for file in files:
                    full_path = os.path.join(subdir, file)
                    s3_client.upload_file(full_path, bucket_name, object_name + file)
                    print(f"Copied {full_path} to {bucket_name} {object_name+file}.")
            return

        if options["download"]:
            file_path = path.join(settings.BASE_DIR, src_path)
            object_name = tgt_path
            s3_client.download_file(bucket_name, object_name, file_path)
            return

        if options["rm"]:
            s3_client.delete_object(
                Bucket=bucket_name,
                Key=tgt_path,
            )
