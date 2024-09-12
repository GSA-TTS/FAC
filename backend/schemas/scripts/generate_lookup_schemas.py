import glob
import json
import pandas as pd
import sys

"""
This script processes CFDA/ALN and cluster name CSV files to generate schema
JSON, and it can be run using `make source_data`. Input files are found in
`schemas/source/data`, and the latest-dated file will be used. To run manually:

`python scripts/generate_lookup_schemas.py <item to process> <output JSON filepath>`

where "item to process" is either "cfda-lookup" or "cluster-names".
"""


def cleanup_string(s):
    s = str(s).strip()
    # Replace two spaces with one
    s = " ".join(s.split())
    return s


def lmap(fun, ls):
    return list(map(fun, ls))


def process_cfda_lookup(file_path):
    df = pd.read_csv(file_path, encoding="utf-8", converters={"Program Number": str})

    # Build a couple of Python objects to render as
    # JSON, and then as Jsonnet
    program_names = list(df["Program Title"])
    program_numbers = list(df["Program Number"])

    unique_prefixes_dict = {}
    unique_cfda_dict = {}

    for program_number in program_numbers:
        prefix, _ = program_number.split(".")
        unique_prefixes_dict[prefix] = None
        unique_cfda_dict[program_number] = None

    unique_prefix_list = list(unique_prefixes_dict.keys())
    unique_cfda_list = list(unique_cfda_dict.keys())

    # Clean everything up
    program_names = lmap(cleanup_string, program_names)
    unique_prefix_list = lmap(cleanup_string, unique_prefix_list)
    unique_cfda_list = lmap(cleanup_string, unique_cfda_list)

    # Enforce upper case
    program_names = lmap(lambda s: s.upper(), program_names)

    return {
        "program_names": program_names,
        "all_alns": unique_cfda_list,
        "aln_prefixes": unique_prefix_list,
    }


def process_cluster_names(filename):
    df = pd.read_csv(filename)
    cluster_names = list(df["NAME"])
    # Clean everything up
    cluster_names = lmap(cleanup_string, cluster_names)
    # Enforce upper case
    cluster_names = lmap(lambda s: s.upper(), cluster_names)

    return {
        "cluster_names": cluster_names,
    }


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        item_to_process = sys.argv[1]
        glob_str = f"./source/data/{item_to_process}-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].csv"

        print(f"Globbing for {glob_str}")

        list_of_files = glob.glob(glob_str)
        print(f"Found {len(list_of_files)} files")

        if not len(list_of_files):
            print(f"No {item_to_process} CSV files found in schemas/source/data/")
            sys.exit(1)

        latest_file = sorted(list_of_files)[-1]
        print(f"Processing latest file {latest_file}")

        obj = None
        match item_to_process:
            case "cfda-lookup":
                obj = process_cfda_lookup(latest_file)
            case "cluster-names":
                obj = process_cluster_names(latest_file)
            case _:
                print("Unknown filename, exiting")
                sys.exit(1)

        with open(sys.argv[2], "w", newline="\n") as write_file:
            json.dump(obj, write_file, indent=2, sort_keys=True)
