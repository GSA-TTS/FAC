import sqlite3
import json
from collections import defaultdict
from pprint import pprint
from datetime import datetime


class FakeSAC:
    pass


def make_fake_sacs(records):
    new_records = []
    for r in records:
        fsac = FakeSAC()
        fsac.report_id = r["report_id"]
        fsac.general_information = dict()
        fsac.general_information["auditee_uei"] = r["auditee_uei"]
        fsac.general_information["ein"] = r["auditee_ein"]
        fsac.general_information["auditee_name"] = r["auditee_name"]
        fsac.general_information["auditee_contact_name"] = r["auditee_contact_name"]
        fsac.general_information["auditee_email"] = r["auditee_email"]
        fsac.general_information["auditee_state"] = r["auditee_state"]

        fsac.general_information["auditor_email"] = r["auditor_email"]
        fsac.general_information["auditor_name"] = r["auditor_contact_name"]

        fsac.general_information["auditee_fiscal_period_end"] = r["fy_end_date"]
        fsac.transition_name = ["submitted"]
        fsac.transition_date = [datetime.strptime(r["submitted_date"], "%Y-%m-%d")]

        new_records.append(fsac)
    return new_records


def fetch_sac_resubmission_records_sqlite(
    AY, sqlite_file, duplication_threshold=2, noisy=False
):

    connection = sqlite3.connect(sqlite_file)
    cursor = connection.cursor()
    rows = cursor.execute(
        f"""
        SELECT json
        FROM raw
        WHERE
            json->>'fy_end_date'
                LIKE '{AY}%'
            AND
            json->>'auditee_uei' != 'GSA_MIGRATION'
        """
    )
    # Those are all of the rows for a year. Pack them into a list.
    raw = []
    records = []
    for row in rows:
        raw.append(json.loads(row[0]))

    print(f"Found {len(raw)} records")

    # Now, count by UEI
    uei_counts = defaultdict(int)
    for row in raw:
        uei_counts[row["auditee_uei"]] += 1

    # And, if they pass the threshold, keep.
    for row in raw:
        if uei_counts[row["auditee_uei"]] >= duplication_threshold:
            records.append(row)
    records = sorted(records, key=lambda r: r["fac_accepted_date"])

    print(f"Processing {len(records)} records")

    sacked = make_fake_sacs(records)
    return sacked
