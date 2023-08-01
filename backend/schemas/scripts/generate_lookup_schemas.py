import pandas as pd
import json
import sys


def cleanup_string(s):
    s = str(s).strip()
    # Replace two spaces with one
    s = " ".join(s.split())
    return s


def lmap(fun, ls):
    return list(map(fun, ls))


def process_cfda_lookup(arg):
    df = pd.read_csv(arg[1], converters={"CFDAEXT": str})
    # Build a couple of Python objects to render as
    # JSON, and then as Jsonnet
    program_names = list(df["FEDERALPROGRAMNAME"])

    unique_prefixes_dict = {}
    for prefix in df["CFDAPREFIX"]:
        unique_prefixes_dict[prefix] = prefix
    unique_prefix_list = list(unique_prefixes_dict.keys())

    unique_cfda_dict = {}
    for index, row in df.iterrows():
        unique_cfda_dict[f"{row['CFDAPREFIX']}.{row['CFDAEXT']}"] = 1
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


def process_cluster_names(arg):
    df = pd.read_csv(arg[1])
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
        lookup_name = sys.argv[1]
        obj = None
        if "cfda-lookup" in lookup_name.lower():
            obj = process_cfda_lookup(sys.argv)
        elif "cluster-names" in lookup_name.lower():
            obj = process_cluster_names(sys.argv)
        # elif "section-names" in lookup_name.lower():
        #     obj = FORM_SECTIONS
        else:
            print("Unknown filename, exiting")
            sys.exit(1)

        with open(sys.argv[2], "w") as write_file:
            json.dump(obj, write_file, indent=2, sort_keys=True)
