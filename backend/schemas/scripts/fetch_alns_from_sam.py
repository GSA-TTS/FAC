import csv
import os
import sys
from pathlib import Path
import requests


BASE_URL = "https://api.sam.gov/assistance-listings/v1/search"
PAGE_SIZE = 100

SCHEMAS_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SCHEMAS_DIR / "source" / "data" / "aln_csvs_to_be_merged"


def fetch_all(api_key: str, status: str):
    records = []
    page_number = 1

    while True:
        params = {
            "api_key": api_key,
            "pageSize": PAGE_SIZE,
            "pageNumber": page_number,
            "status": status,
        }

        response = requests.get(BASE_URL, params=params, timeout=60)

        if response.status_code != 200:
            raise RuntimeError(
                f"SAM.gov API error for {status} page {page_number}: {response.status_code}"
            )

        data = response.json()
        page_records = data.get("assistanceListingsData", [])

        print(f"Fetched {status} page {page_number}: {len(page_records)} records")

        records.extend(page_records)

        total_pages = data.get("totalPages", page_number)
        if page_number >= total_pages:
            break

        page_number += 1

    return records


def write_csv(records, output_file: Path):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    rows = sorted(
        [
            {
                "Program Title": (r.get("title") or "").strip(),
                "Program Number": (r.get("assistanceListingId") or "").strip(),
            }
            for r in records
            if r.get("assistanceListingId") and r.get("title")
        ],
        key=lambda x: x["Program Number"],
    )

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Program Title", "Program Number"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_file}")


def main():
    api_key = os.getenv("SAM_API_KEY")

    if not api_key:
        print("Missing SAM_API_KEY", file=sys.stderr)
        sys.exit(1)

    active = fetch_all(api_key, "Active")
    inactive = fetch_all(api_key, "Inactive")

    write_csv(active, OUTPUT_DIR / "active-alns.csv")
    write_csv(inactive, OUTPUT_DIR / "inactive-alns.csv")


if __name__ == "__main__":
    main()