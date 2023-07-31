from collections import OrderedDict
import csv
import glob
import json
import _jsonnet
import os


# Pull in agency names from the most recent cfda-agencies-YYYYMMDD.csv
# Scraps rows with non-int agency nums and rows with empty agency names.
def get_agency_names():
    # Lets build a dictionary of names, mapping the agency number
    # to the name.
    _agency_names = dict()
    agency_names = OrderedDict()
    # Grab all the files, but we'll then sort and grab the latest one.
    # MCJ: We need to figure out how to keep ALNs up-to-date...
    # https://github.com/GSA-TTS/FAC/issues/1555
    list_of_files = glob.glob("./schemas/source/data/cfda-agencies*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)

    with open(latest_file, "r") as file:
        csvreader = csv.reader(file)
        csvreader = sorted(csvreader, key=lambda x: x[0])
        for row in csvreader:
            if row[0].isnumeric() and row[1] != "":
                _agency_names[row[0]] = row[1]
    # Now, create an OrderedDict of all the values
    agency_names = OrderedDict(sorted(_agency_names.items(), key=lambda tupl: tupl[0]))

    return agency_names


def get_gaap_results():
    sonnet = "./schemas/source/base/GAAP.libsonnet"
    json_str = _jsonnet.evaluate_snippet(sonnet, open(sonnet).read())
    jobj = json.loads(json_str)
    # Returns a list of dictionaries with the keys 'tag' and 'readable'
    return jobj["gaap_results"]
