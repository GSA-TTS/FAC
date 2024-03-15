import logging
import boto3
import requests
import os
import json

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
            timeout=30,
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
    pages = paginator.paginate(Bucket=bucket, Prefix=path)
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


# The VCAP_SERVICES for S3 instances looks like this:
# "s3": [
#     {
#         "label": "s3",
#         "provider": null,
#         "plan": "basic",
#         "name": "backups",
#         "tags": [
#             "AWS",
#             "S3",
#             "object-storage"
#         ],
#         "instance_guid": "UUID",
#         "instance_name": "backups",
#         "binding_guid": "UUID",
#         "binding_name": null,
#         "credentials": {
#             "uri": "s3://KEYID:SECKEY@s3-us-gov-west-1.amazonaws.com/cg-BUCKET",
#             "insecure_skip_verify": false,
#             "access_key_id": "KEYID",
#             "secret_access_key": "SECKEY",
#             "region": "us-gov-west-1",
#             "bucket": "cg-BUCKET",
#             "endpoint": "s3-us-gov-west-1.amazonaws.com",
#             "fips_endpoint": "s3-fips.us-gov-west-1.amazonaws.com",
#             "additional_buckets": []
#         },
#         "syslog_drain_url": null,
#         "volume_mounts": []
#     }, ...


def lookup_bucket_in_vcap(friendly_bucket):
    vcap_services = json.loads(os.getenv("VCAP_SERVICES"))
    for instance in vcap_services["s3"]:
        if instance["instance_name"] == friendly_bucket:
            return instance["credentials"]["bucket"]
    # If we get here, it is bad.
    logger.error("======================================")
    logger.error("Could not get bucket name in production environment.")
    logger.error("Exiting.")
    logger.error("======================================")
    os.exit(-1)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--bucket", type=str, required=True)
        parser.add_argument("--object", type=str, required=False, default=None)
        parser.add_argument(
            "--paths", type=str, nargs="+", required=False, default=None
        )
        pass

    def handle(self, *args, **options):
        bucket = options["bucket"]
        object = options["object"]
        paths = options["paths"]

        # The bucket name is a "friendly" name.
        # We need to look it up in VCAP_SERVICES if we are not local, and
        # then convert it to the brokered name.
        if os.getenv("ENV") not in ["LOCAL", "TESTING"]:
            brokered_bucket = lookup_bucket_in_vcap(bucket)
            bucket = brokered_bucket

        # Do we want to scan a single object?
        if object:
            result = scan_file_in_s3(bucket, object)
            if check_scan_ok(result):
                pass
            else:
                logger.error(f"SCAN FAIL: {object}")
        if paths:
            all_results = {}
            for path in paths:
                results = scan_files_at_path_in_s3(bucket, path)
                for key in ["good_count", "bad_count"]:
                    all_results[key] = results[key] + all_results.get(key, 0)
            logger.info(
                "SCAN OK: PATH %s COUNT passed: %s, failed: %s",
                path,
                all_results["good_count"],
                all_results["bad_count"],
            )
