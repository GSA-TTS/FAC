"""
Read files from a specified folder in the Census S3 folder,
Cclean them and 
Ceate a PG table
"""

import logging
import boto3
import io


from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
)
c2f_bucket_name = settings.AWS_C2F_BUCKET_NAME


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--folder", help="S3 folder name", required=True)

    def handle(self, *args, **options):
        items = s3_client.list_objects(
            Bucket=c2f_bucket_name,
            Prefix=options["folder"],
        )["Contents"]
        for item in items:
            print(item["Key"], item["Size"], item["LastModified"])
            table_name = self.create_table(item["Key"])
            response = s3_client.get_object(Bucket=c2f_bucket_name, Key=item["Key"])
            rows = io.BytesIO(response["Body"].read())
            self.load_table(table_name, rows)

    def create_table(self, name):
        print(f"Creating table {name}")
        return name

    def load_table(self, table_name, rows):
        row_list = list(rows)
        print(f"Loading {len(row_list)} rows into {table_name}")
        for i in range(5):
            print(row_list[i])
