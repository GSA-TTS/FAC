import glob
import logging
import requests
import timeit
from io import BytesIO

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


logger = logging.getLogger(__name__)


class ClamAVError(Exception):
    def __init__(self, file):
        self.file = file

    def __str__(self):
        return "Static virus scan failed"


def _scan_file(file, filepath):
    try:
        logger.info(f"Scanning {filepath}")
        return requests.post(
            settings.AV_SCAN_URL,
            files={"file": file},
            data={"name": filepath},
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        logger.error("SCAN Connection error")
        raise ClamAVError(filepath)
    except Exception as e:
        logger.error(f"SCAN EXCEPTION UNKNOWN {filepath} {e}")
        raise ClamAVError(filepath)


def scan_file(filepath):
    try:
        with open(filepath, "rb") as fh:
            file = BytesIO(fh.read())
            return _scan_file(file, filepath)
    except Exception as e:
        logger.error(f"SCAN SCAN_FILE {e}")


def scan_files_at_path(path, num_to_scan):
    good_count, bad_count = 0, 0
    filepaths = glob.glob(path + '*')
    num_scanned = 0

    while num_scanned < num_to_scan:
        # Short circuits scans when we have more files than needed
        filepaths_to_scan = filepaths[:num_to_scan-num_scanned]

        for filepath in filepaths_to_scan:
            result = scan_file(filepath)

            if not check_scan_ok(result):
                logger.error("SCAN revealed potential infection, %s", result)
                bad_count = bad_count + 1
            else:
                good_count = good_count + 1

            num_scanned = good_count + bad_count

    return {"good_count": good_count, "bad_count": bad_count}


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
        parser.add_argument("--path", type=str, required=True, default=None)
        parser.add_argument("--num_to_scan", type=int, required=False, default=1)
        pass

    def handle(self, *args, **options):
        path = options["path"]
        num_to_scan = options["num_to_scan"]
        results = scan_files_at_path(path, num_to_scan)

        logger.info(
            "SCAN OK: COUNT passed: %s, failed: %s",
            results["good_count"],
            results["bad_count"],
        )
