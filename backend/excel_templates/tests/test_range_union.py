import json
import _jsonnet
import os

excel_path = "definitions"
schema_path = "../schemas/sources"

test_table = [
    {
        "excel": "federal-awards-expended-template-20230425.jsonnet", 
        "schema": "FederalAwards.schema.jsonnet",
        "ignore_in_schema": set([
            "cluster", 
            "direct_or_indirect_award", 
            "loan_or_loan_guarantee",
            "program",
            "subrecipients",
            "entities"
            ])
    },
]

def jsonnet_sheet_spec_to_json(filename):
    print(os.getcwd())
    json_str = _jsonnet.evaluate_snippet(filename, open(filename).read())
    jobj = json.loads(json_str)
    return jobj

def extract_ranges_from_excel_def(filename) -> set:
    jobj = jsonnet_sheet_spec_to_json(filename)
    range_names = set()
    sheets = jobj['sheets']
    for sheet in sheets:
        singles = sheet["single_cells"]
        ranges  = sheet["open_ranges"]
        for s in singles:
            range_names.add(s["range_name"])
        for r in ranges:
            range_names.add(r["range_name"])
    return range_names

def recursively_find_properties(obj):
    found = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "properties":
                for p, v in obj[k].items():
                    found.add(p)
                    found.update(recursively_find_properties(v))
            found.update(recursively_find_properties(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(recursively_find_properties(item))
    return found

def extract_ranges_from_schema(root, filename) -> set:
    jobj = jsonnet_sheet_spec_to_json(filename)
    found = recursively_find_properties(jobj["properties"][root]["properties"])
    return found
        
def test_federal_awards_named_ranges():
    for d in test_table:
        excel_ranges = extract_ranges_from_excel_def(os.path.join(os.getcwd(), excel_path, d["excel"]))
        schema_ranges = extract_ranges_from_schema("FederalAwards", os.path.join(os.getcwd(), schema_path, d["schema"]))
        schema_ranges.difference_update(d["ignore_in_schema"])
        ediff = excel_ranges.difference(schema_ranges)
        sdiff = schema_ranges.difference(excel_ranges)
        print("SHEET")
        print(excel_ranges)
        print("SCHEMA")
        print(schema_ranges)
        print("IN BOTH")
        print(schema_ranges.intersection(excel_ranges))
        if ediff != set():
            print(f"Sheet contains extra ranges: {ediff}")
        if sdiff != set():
            print(f"Schema contains extra rows: {sdiff}")
        assert ediff == set()
        assert sdiff == set()
