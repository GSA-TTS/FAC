# Run this as

# python create_stream_yaml.py > public_data_v1_0_0_single_csv.yaml

# to regenerate the sling file.

import yaml
from pprint import pprint

obj = {"streams": dict()}

obj["source"] = "FAC_SNAPSHOT_URI"
obj["target"] = "BULK_DATA_EXPORT"
obj["defaults"] = {
    "target_options": {
        "format": "csv",
        "compression": "gzip",
        "file_max_rows": 0,
    }
}

schema = "public_data_v1_0_0"

tables = [
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

years = range(2016, 2031)


for t in tables:
    ndx = 0
    for y in years:
        obj["streams"][f"{schema}.{t}.{ndx}"] = {
            "object": f"bulk_export/{{MM}}/{t}_{y}.csv",
            "sql": f"SELECT * FROM {schema}.{t} WHERE audit_year = '{y}'",
            "mode": "full-refresh",
        }
        ndx += 1

print(yaml.dump(obj))
