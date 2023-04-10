import os
import logging
import boto3
from botocore.exceptions import ClientError

from django.core.management.base import BaseCommand
from django.conf import settings

from data_distro import models as mods

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Moves PDFs from source bucket to the bucket in the env.

    To run the script, add the Census AWS values to the environment.
    In cloud.gov use UUPS, you will need to include the existing env in
    the commands https://cli.cloudfoundry.org/en-US/v6/update-user-provided-service.html.

    Then, you can run the script by pushing a task runner to cloud.gov and giving ith the add_pdfs
    management command.

    Update public_doc_query once we know how to determine the mapping of records to PDFs.
    Create a private_doc_query() and call add_to_private() for non-public PDFs.
    """

    def handle(self, *args, **kwargs):
        public_doc_records = public_doc_query()
        for doc in public_doc_records:
            pdf_name = doc["pdf_name"]
            # We don't want to delete the original so we are not moving and we can't rename and copy at the same time
            try:
                temp_name = grab_doc(pdf_name)
                add_me = True
            except ClientError:
                add_me = False
                logger.error(f"DOWNLOAD FAILED: {pdf_name}")

            if add_me is True:
                url = add_to_public(
                    pdf_name, doc["audit_year"], doc["dbkey"], temp_name
                )
                add_to_model(doc["id"], url)


def public_doc_query():
    # UPDATE THIS to mapping of PDF url
    # Filter out records that already have pdfs
    # records = mods.General.objects.filter(is_public=True).values('audit_year', 'dbkey', 'id')

    # Bogus Test record
    test_records = [
        {
            "audit_year": "2022",
            "dbkey": "101786",
            "pdf_name": "1002792007.pdf",
            "id": 1,
        }
    ]
    return test_records


def grab_doc(pdf_name):
    temp_name = "data_distro/data_to_load/{}".format(pdf_name)
    census_bucket = settings.AWS_CENSUS_STORAGE_BUCKET_NAME
    AWS_S3_CREDS = {
        "aws_access_key_id": settings.AWS_CENSUS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_CENSUS_SECRET_ACCESS_KEY,
        "region_name": settings.AWS_S3_CENSUS_REGION_NAME,
    }
    s3 = boto3.client("s3", **AWS_S3_CREDS)
    s3.download_file(census_bucket, pdf_name, temp_name)

    return temp_name


def add_to_public(pdf_name, audit_year, dbkey, temp_name):
    public_bucket = settings.AWS_STORAGE_BUCKET_NAME
    AWS_S3_CREDS = {
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
        "region_name": settings.AWS_S3_REGION_NAME,
    }
    s3_client = boto3.client("s3", **AWS_S3_CREDS)
    new_file_name = f"collections/{audit_year}/pdf/{dbkey}-{pdf_name}"
    s3_client.upload_file(temp_name, public_bucket, new_file_name)
    os.remove(new_file_name)

    url = f"https://{public_bucket}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{new_file_name}"
    return url


def add_to_private(pdf_name, audit_year, dbkey, temp_name):
    private_bucket = settings.AWS_PRIVATE_STORAGE_BUCKET_NAME
    AWS_S3_CREDS = {
        "aws_access_key_id": settings.AWS_PRIVATE_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
        "region_name": settings.AWS_S3_PRIVATE_REGION_NAME,
    }
    s3_client = boto3.client("s3", **AWS_S3_CREDS)
    new_file_name = f"collections/{audit_year}/pdf/{dbkey}-{pdf_name}"
    s3_client.upload_file(temp_name, private_bucket, new_file_name)
    os.remove(new_file_name)

    url = f"https://{private_bucket}.s3.{settings.AWS_S3_PRIVATE_REGION_NAME}.amazonaws.com/{new_file_name}"
    return url


def add_to_model(id, url):
    record = mods.General.objects.get(id=id)
    record.pdf_urls = [url]
    record.save()
