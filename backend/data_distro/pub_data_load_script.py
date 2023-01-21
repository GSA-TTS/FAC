"""
Download data from https://facdissem.census.gov/PublicDataDownloads.aspx
Then unzip the files and place the them in data_distro/data_to_load/
"""
import csv
import re
from os import walk, system
import traceback
from pandas import read_csv

# from models.py import *
# from download_model_dictonaries import model_title_transforms, field_transforms
from data_distro import models as mods
from data_distro.download_model_dictonaries import (
    model_title_transforms,
    field_transforms,
    table_mappings,
    field_mappings,
    boolen_fields,
)

# Special conversions
boolean_conversion = {"Y":True, "N":False}

# Grab just the files we want, no ds_store etc
def file_clean(all_file_names):
    table_names = list(table_mappings.keys())
    file_names = []
    for f in all_file_names:
        # I am starting with loading from the FY 22 downloads
        name = f.replace("22.txt", "")
        if name in table_names:
            file_names.append(f)
    return file_names

# agency22.txt, captext_formatted22.txt works
# agency22.txt, captext_formatted22.txt works
# load_file_names = ['cfda22.txt', 'cpas22.txt', 'duns22.txt', 'eins22.txt', 'findings22.txt', 'findingstext_formatted22.txt', 'gen22.txt', 'notes22.txt', 'passthrough22.txt', 'revisions22.txt', 'ueis22.txt']


# Load files into django models
def load_files(load_file_names):
    # for file_path in temp_files:


for f in load_file_names:
    file_path = "data_distro/data_to_load/{}".format(f)
    file_name = file_path.replace("data_distro/data_to_load/", "")
    table = re.sub("22.txt", "", file_name)
    print("-----", table)
    print("Starting {0}...".format(file_name))
    fac_model_name = table_mappings[table]
    fac_model = getattr(mods, fac_model_name)
    for i, chunk in enumerate(read_csv(file_path, chunksize=35000, sep="|", encoding="mac-roman")):
        csv_dict = chunk.to_dict(orient='records')
        for row in csv_dict:
            # try:
            fields = list(row.keys())
            instance_dict = {}
            # should do this with the header instead
            for key in fields:
                field_name = field_mappings[key]
                payload = row[key]
                # break cleaning logic into a separate function
                if field_name in boolen_fields:
                    payload = boolean_conversion.get(payload, None)
                if field_name == "cfda":
                    payload = str(payload)
                instance_dict[field_name] = payload
            print(instance_dict)
            p, created = fac_model.objects.get_or_create(**instance_dict)
            # p.save()
            # print("~~~~~~~~~~~~~~~~~~worked~~~~~~~~~~~~~~~~~~~~~~~~~~~")

            except Exception:
                print("---------------------PROBLEM---------------------")
                print(table, file_path)
                print("----", instance_dict,"----")
                print(row)
                print("~~~~~")
                traceback.print_exc()
                print("-------------------------------------------------")
                continue
    print("Finished {0}".format(file_name))

def load_data():
    """
     1) Find all the files for upload
     2) Grab just the files we want
     3) Load data into Django models
    """
    all_file_names = next(walk("data_distro/data_to_load"), (None, None, []))[2]
    load_file_names = file_clean(all_file_names)
    load_files(temp_files)

load_data()
