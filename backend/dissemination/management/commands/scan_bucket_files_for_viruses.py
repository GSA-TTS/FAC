import logging
import boto3
import requests
from io import BytesIO
from botocore.client import ClientError, Config

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

logger = logging.getLogger(__name__)


class ClamAVError(Exception):
    def __init__(self, file):
        self.file = file

    def __str__(self):
        return "Static virus scan failed"


def _scan_file(file):
    try:
        return requests.post(
            settings.AV_SCAN_URL,
            files={"file": file},
            data={"name": file.name},
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        logger.error("SCAN Connection error")
        raise ClamAVError(file.name)
    except Exception as e:
        logger.error(f"SCAN EXCEPTION UNKNOWN {file} {e}")
        raise ClamAVError(file.name)


def get_s3_client():
    s3 = boto3.client(
        service_name="s3",
        region_name=settings.AWS_S3_PRIVATE_REGION_NAME,
        aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_PRIVATE_INTERNAL_ENDPOINT,
        config=Config(signature_version="s3v4"),
    )
    return s3


# Loads a file from S3 into a BytesIO object.
# This is file-like, and can be used for passing on
# to a POST to ClamAV.
def load_file_from_s3(bucket, object_name):
    s3 = get_s3_client()
    file = BytesIO()
    try:
        s3.download_fileobj(bucket, object_name, file)
    except ClientError:
        logger.error("======================================")
        logger.error(f"Could not download {object_name}")
        logger.error("======================================")
        return None
    except Exception as e:
        logger.error("======================================")
        logger.error(f"{e}")
        logger.error("======================================")
        return None

    # Seek to the start of the file.
    file.seek(0)
    return file


def scan_file_in_s3(bucket, object_name):
    try:
        io_obj = load_file_from_s3(bucket, object_name)
        bytes_blob = io_obj.read()
        simple_obj = SimpleUploadedFile(object_name, bytes_blob)
        return _scan_file(simple_obj)
    except Exception as e:
        logger.error(f"SCAN SCAN_FILE_IN_S3 {e}")
        return f"{object_name}"


def scan_files_at_path_in_s3(bucket, path):
    s3 = get_s3_client()
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket="bucket", Prefix="prefix")
    good_count, bad_count = 0, 0

    if pages:
        for page in pages:
            if "Contents" in page:
                for object_summary in page["Contents"]:
                    object_name = object_summary["Key"]
                    result = scan_file_in_s3(bucket, object_name)
                    if not check_scan_ok(result):
                        logger.error("SCAN revealed potential infection, %s", result)
                        bad_count = bad_count + 1
                    else:
                        good_count = good_count + 1
        return {"good_count": good_count, "bad_count": bad_count}

    logger.error(
        "SCAN NO PAGES: No pages found for bucket %s and path %s", bucket, path
    )


def is_stringlike(o):
    return isinstance(o, str) or isinstance(o, bytes)


def not_a_stringlike(o):
    return not is_stringlike(o)


def check_scan_ok(result):
    if result and not_a_stringlike(result) and result.status_code == 200:
        return True
    else:
        return False


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--bucket", type=str, required=True)
        parser.add_argument("--object", type=str, required=False, default=None)
        parser.add_argument("--path", type=str, required=False, default=None)
        pass

    def handle(self, *args, **options):
        bucket = options["bucket"]
        object = options["object"]
        path = options["path"]

        # Do we want to scan a single object?
        if object:
            result = scan_file_in_s3(bucket, object)
            if check_scan_ok(result):
                pass
            else:
                logger.error(f"SCAN FAIL: {object}")
        if path:
            results = scan_files_at_path_in_s3(bucket, path)
            logger.info(
                "SCAN OK: COUNT passed: %s, failed: %s",
                results["good_count"],
                results["bad_count"],
            )
