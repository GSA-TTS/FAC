import pandas as pd
import json
import sys


def cleanup_string(s):
    s = str(s).strip()
    # Replace two spaces with one
    s = ' '.join(s.split())
    return s


def lmap(fun, ls):
    return list(map(fun, ls))


if __name__ == "__main__":
    if len(sys.argv) == 3:
        df = pd.read_csv(sys.argv[1], converters={'CFDAEXT': str})
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

        # print(program_names.values[0:10])
        # print(unique_cfda_list[0:10])

        # Clean everything up
        program_names = lmap(cleanup_string, program_names)
        unique_prefix_list = lmap(cleanup_string, unique_prefix_list)
        unique_cfda_list = lmap(cleanup_string, unique_cfda_list)

        obj = {
            "program_names": program_names,
            "all_alns": unique_cfda_list,
            "aln_prefixes": unique_prefix_list,

        }

        with open(sys.argv[2], "w") as write_file:
            json.dump(obj, write_file, indent=2, sort_keys=True)
