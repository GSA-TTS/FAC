import csv
import os
import sys
from pathlib import Path

import requests

BASE_URL = "https://api.sam.gov/assistance-listings/v1/search"
PAGE_SIZE = 100

SCHEMAS_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SCHEMAS_DIR / "source" / "data" / "aln_csvs_to_be_merged"


def fetch_all(api_key: str, status: str) -> list[dict]:
    records = []
    page_number = 1
    more_pages_to_read = True

    # Create session ONCE (important)
    session = requests.Session()

    while more_pages_to_read:
        params: dict[str, str | int] = {
            "api_key": api_key,
            "pageSize": PAGE_SIZE,
            "pageNumber": page_number,
            "status": status,
        }

        print(f"Requesting {status} page {page_number}...")

        response = session.get(BASE_URL, params=params, timeout=(5, 20))

        if response.status_code != 200:
            raise RuntimeError(
                f"SAM.gov API error for {status} page {page_number}: "
                f"{response.status_code} - {response.text}"
            )

        data = response.json()
        page_records = data.get("assistanceListingsData", [])
        total_pages = data.get("totalPages", page_number)

        print(
            f"Fetched {status} page {page_number} of {total_pages}: "
            f"{len(page_records)} records"
        )

        records.extend(page_records)

        if page_number >= total_pages:
            more_pages_to_read = False
        else:
            page_number += 1

    return records


def write_csv(records: list[dict], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    rows = sorted(
        [
            {
                "Program Title": (record.get("title") or "").strip(),
                "Program Number": (record.get("assistanceListingId") or "").strip(),
            }
            for record in records
            if record.get("assistanceListingId") and record.get("title")
        ],
        key=lambda row: row["Program Number"],
    )

    with output_file.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["Program Title", "Program Number"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_file}")


def main() -> None:
    api_key = os.getenv("SAM_API_KEY")

    if not api_key:
        print("Missing SAM_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    active_records = fetch_all(api_key, "Active")
    inactive_records = fetch_all(api_key, "Inactive")

    write_csv(active_records, OUTPUT_DIR / "active-alns.csv")
    write_csv(inactive_records, OUTPUT_DIR / "inactive-alns.csv")


if __name__ == "__main__":
    main()
