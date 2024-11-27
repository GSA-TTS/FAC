# Run this as

# python create_stream_yaml.py > public_data_v1_0_0_single_csv.yaml

# to regenerate the sling file.

import yaml
from datetime import datetime

obj: dict = {
    "streams": {},
    "source": "FAC_SNAPSHOT_URI",
    "target": "BULK_DATA_EXPORT",
    "defaults": {
        "target_options": {
            "format": "csv",
            "compression": "gzip",
            "file_max_rows": 0,
        }
    },
}

SCHEMA = "public_data_v1_0_0"

TABLES = [
    "additional_eins",
    "additional_ueis",
    "combined",
    "corrective_action_plans",
    "federal_awards",
    "findings",
    "findings_text",
    "general",
    "notes_to_sefa",
    "passthrough",
    "secondary_auditors",
]

# Although this attempts to generate files all the way out to 2030,
# it will not generate anything where data does not exist.
# This future-proofs us for a year or two, so we don't have to worry
# about updating the `sling` script that is created.
YEARS = range(2016, 2031)


for t in TABLES:
    ndx = 0
    for y in YEARS:
        obj["streams"][f"{SCHEMA}.{t}.{ndx}"] = {
            "object": f"bulk_export/{{MM}}/{y}_{t}.csv",
            "sql": f"SELECT * FROM {SCHEMA}.{t} WHERE audit_year = '{y}'",
            "mode": "full-refresh",
            "target_options": {
                "format": "csv",
            },
        }
        ndx += 1

today = datetime.today().strftime("%Y-%m-%d")
print("# DO NOT EDIT; THIS IS A GENERATED FILE")
print("# python create_stream_yaml.py > public_data_v1_0_0_single_csv.yaml")
print(f"# Last generated {today}")
print()
print(yaml.dump(obj))
