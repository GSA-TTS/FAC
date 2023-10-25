import logging

# import requests
import zipfile

# import io
import os
import boto3

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
        parser.add_argument("--zip_url", help="Remote file name")
        parser.add_argument("--zip_src", help="local file name.")

    def handle(self, *args, **options):
        url = options["zip_url"]
        src = options["zip_src"]
        if not url and not src:
            logger.error("Remote or local zip file must be specified")
            return
        if url:
            print("Not yet implemented")
            return

        folder, zip_file = self.get_folder_and_file(url, src)
        for file_name in zip_file.namelist():
            tgt_path = f"{folder}/{file_name}"
            with zip_file.open(file_name, "r") as zip_object:
                s3_client.upload_fileobj(zip_object, c2f_bucket_name, tgt_path)
            print(f"Uploaded : {tgt_path} ")

    def get_folder_and_file(self, url, src):
        if url:
            print("Not yet implemented")

            # response = requests.get(url)
            # if response.status_code != 200:
            #     logger.error(f"Unable to read from {url}. Response =  {response}")
            #     return
            # folder = url.split("/")[-1]
            # zip_file = zipfile.ZipFile(io.BytesIO(response.content))

        if src:
            folder = os.path.basename(src).split(".")[0]
            zip_file = zipfile.ZipFile(src)

        return folder, zip_file
