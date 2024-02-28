import argparse
import glob
import logging
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO


logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])


class ClamAVError(Exception):
    def __init__(self, file):
        self.file = file

    def __str__(self):
        return "Static virus scan failed"


def _scan_file(file, filepath):
    try:
        logging.info(f"Scanning {filepath}")
        return requests.post(
            "http://clamav-rest:9000/scan",
            files={"file": file},
            data={"name": filepath},
            timeout=300,
        )
    except requests.exceptions.ConnectionError:
        logging.error("SCAN Connection error")
        raise ClamAVError(filepath)
    except Exception as e:
        logging.error(f"SCAN EXCEPTION UNKNOWN {filepath} {e}")
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
        logging.error(f"SCAN SCAN_FILE {e}")


def scan_files_at_path(path, num_to_scan, max_workers):
    filepaths = glob.glob(path + "*")[:num_to_scan]
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


def main():
    """
    Outputs metrics from performing ClamAV file scans. Beware: ClamAV must be restarted
    between runs of this script (`docker restart backend-clamav-rest-1`) in order to
    clear the file cache.
    Usage:
    python collect_scan_metrics --path <path pattern> --num_to_scan <int> --num_workers <int>
    Example:
    python collect_scan_metrics --path 'metrics_files/*.xlsx' --num_to_scan 20 --num_workers 5
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--path", type=str, required=True, default=None)
    parser.add_argument("--num_to_scan", type=int, required=False, default=1)
    parser.add_argument("--num_workers", type=int, required=False, default=1)

    args = parser.parse_args()

    path = args.path
    num_to_scan = args.num_to_scan
    num_workers = args.num_workers

    t1 = time.perf_counter(), time.process_time()
    results = scan_files_at_path(path, num_to_scan, num_workers)
    t2 = time.perf_counter(), time.process_time()
    real_time = t2[0] - t1[0]

    logging.info(f"Num files: {num_to_scan}")
    logging.info(f"Num workers: {num_workers}")
    logging.info(f"Real time: {real_time / 60} minutes")
    logging.info(f"Total time: {sum(results) / 60} minutes")
    logging.info(f"Max time: {max(results)} seconds")
    logging.info(f"Avg time: {sum(results) / len(results)} seconds")


if __name__ == "__main__":
    main()
