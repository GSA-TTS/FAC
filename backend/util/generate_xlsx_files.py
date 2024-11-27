import argparse
import datetime
import logging
import openpyxl
import os
import sys


logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])


def generate_files(base_xlsx, num_files, output):
    logging.info(f"Loading base XLSX {base_xlsx}...")

    wb = openpyxl.load_workbook(base_xlsx)
    ws = wb.active

    logging.info(f"Creating {num_files} files from {base_xlsx} in {output}")

    for i in range(num_files):
        dt = datetime.datetime.now()
        ws["A1"] = dt
        path = os.path.join(output, f"{dt}.xlsx")
        wb.save(path)
        logging.info(f"#{i + 1} Created: {path}")

    logging.info("Done")


def main():
    """
    Generates unique XLSX files by slightly modifying copies of the given a base file. Used in conjuction with the
    collect_scan_metrics cmd.
    Usage:
    python tools/generate_xlsx_files.py --base_xlsx <xlsx file path> --num_files <int>
    Example:
    python tools/generate_xlsx_files.py --base_xlsx 'output/181744-22/federal-awards-workbook-181744.xlsx' --num_files 5
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--output", type=str, required=False, default="./metrics_files")
    parser.add_argument("--base_xlsx", type=str, required=True, default=None)
    parser.add_argument("--num_files", type=int, required=False, default=1)

    args = parser.parse_args()

    output = args.output
    base_xlsx = args.base_xlsx
    num_files = args.num_files

    if not os.path.exists(output):
        try:
            os.mkdir(output)
            logging.info(f"Made directory {output}")
        except Exception as e:
            logging.error(f"Could not create directory {output}: {e}")
            sys.exit()

    if not os.path.exists(base_xlsx):
        logging.error(f"Given base_xlsx {base_xlsx} does not exist")
        sys.exit()

    generate_files(base_xlsx, num_files, output)


if __name__ == "__main__":
    main()
