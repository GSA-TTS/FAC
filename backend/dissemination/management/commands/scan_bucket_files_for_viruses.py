import logging
import boto3
import requests
from io import BytesIO
from botocore.client import ClientError, Config

from config.settings import ENVIRONMENT
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

logger = logging.getLogger(__name__)

class ClamAVError(Exception):
    def __init__(self, file):
        self.file = file

    def __str__(self):
        return f"Static virus scan failed: {self.file}"


def _scan_file(file):
    try:
        return requests.post(
            settings.AV_SCAN_URL,
            files={"file": file},
            data={"name": file.name},
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        raise ClamAVError(file)
    except Exception:
        logger.debug(f"Could not scan {file}")
        raise ClamAVError(file)

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
        logger.info("======================================")
        logger.error("Could not download {}".format(object_name))
        logger.info("======================================")
        return None
    except Exception as e:
        logger.info("======================================")
        logger.error(e)
        logger.info("======================================")
        return None
    
    # Seek to the start of the file.
    file.seek(0)
    return file

def scan_file_in_s3(bucket, object_name):
    try:
        io_obj = load_file_from_s3(bucket, object_name)
        bytes_blob = io_obj.read()
        result = _scan_file(SimpleUploadedFile(bytes_blob, str.encode(object_name)))
        return result
    except Exception as e:
        # logger.error(f"SCAN FAIL: {object_name}")
        return object_name

def scan_files_at_path_in_s3(bucket, path):
    s3 = get_s3_client()
    objects = s3.list_objects(Bucket=bucket, Prefix=path)
    if objects:
        results = []
        for object_summary in objects["Contents"]:
            object_name = object_summary["Key"]
            result = scan_file_in_s3(bucket, object_name)
            results.append(result)
        return results
    return None

def check_scan_ok(result):
    if result and not isinstance(result, str) and result.status_code == 200:
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
                logger.info("SCAN OK")
            else:
                logger.error(f"SCAN FAIL: f{object}")
        if path:
            results = scan_files_at_path_in_s3(bucket, path)
            if all(map(check_scan_ok, results)):
                logger.info(f"SCAN OK: COUNT {len(results)}")
            else:
                for r in results:
                    if isinstance(r, str):
                        logger.error(f"SCAN FAIL: {r}")
