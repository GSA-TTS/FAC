from pathlib import Path
import csv
import glob
import json
import os


def get_agency_names():
    """
    From a CSV of agency data, return a dictionary with the agency codes as
    keys and the names as values, in order:

        {
            "00": "None",
            "01": "African Development Foundation",
            "02": "Agency for International Development",
            …
            "97": "Department of Homeland Security",
            "98": "Agency for International Development",
            "99": "Miscellaneous",
        }

    Pull in agency names from the most recent cfda-agencies-YYYYMMDD.csv
    Scrap rows with non-numeric agency nums and rows with empty agency names.
    """
    # Grab all the files, but we'll then sort and grab the latest one.
    # MCJ: We need to figure out how to keep ALNs up-to-date...
    # https://github.com/GSA-TTS/FAC/issues/1555
    list_of_files = glob.glob("./schemas/source/data/cfda-agencies*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)

    with open(latest_file, "r", newline="", encoding="UTF-8") as file:
        agencies = csv.reader(file)
        sorted_agencies = sorted(agencies, key=lambda x: x[0])

    valid_agencies = filter(lambda r: r[0].isnumeric() and r[1] != "", sorted_agencies)
    return {row[0]: row[1] for row in valid_agencies}


def get_audit_info_lists(name):
    """
    Get lists of internal values and friendly strings for the responses to the
    Audit Information form section.

    Filter out anything with historical_only set to true.

    get_audit_info_lists("gaap_results")
    =>
    [
        {
            "value": "Unmodified opinion",
            "key": "unmodified_opinion",
            "property": "UNMODIFIED_OPINION"
        },
        …
    ]
    """
    jsonfile = Path("./schemas/source/audit/audit-info-values.json")
    jobj = json.loads(jsonfile.read_text(encoding="UTF-8"))

    return [info for info in jobj[name] if not info.get("historical_only") is True]
