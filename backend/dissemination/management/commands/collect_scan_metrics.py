import glob
import logging
import requests
import time
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

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
            timeout=300,
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

        t1 = time.perf_counter(), time.process_time()
        _scan_file(file, filepath)
        t2 = time.perf_counter(), time.process_time()

        return t2[0] - t1[0]
    except Exception as e:
        logger.error(f"SCAN SCAN_FILE {e}")


def scan_files_at_path(path, num_to_scan, max_workers):
    filepaths = glob.glob(path + '*')[:num_to_scan]
    if not filepaths:
        raise Exception(f"No files found at {path}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(scan_file, filepaths))


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
    help = """
        Outputs metrics from performing ClamAV file scans
        Usage:
        manage.py collect_scan_metrics --path <path pattern> --num_to_scan <int>
        Example:
        manage.py collect_scan_metrics --path 'audit/fixtures/*.pdf' --num_to_scan 20
    """

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, required=True, default=None)
        parser.add_argument("--num_to_scan", type=int, required=False, default=1)
        parser.add_argument("--num_workers", type=int, required=False, default=1)
        pass

    def handle(self, *args, **options):
        path = options["path"]
        num_to_scan = options["num_to_scan"]
        num_workers = options["num_workers"]

        results = scan_files_at_path(path, num_to_scan, num_workers)
        logger.info(f"Num files: {num_to_scan}")
        logger.info(f"Num workers: {num_workers}")
        logger.info(f"Total time: {sum(results)} seconds")
        logger.info(f"Max time: {max(results)} seconds")
        logger.info(f"Avg time: {sum(results) / len(results)} seconds")

