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

# Separate files into manageable sizes
def nomalize_csvs(load_file_names):
    temp_files = []
    system('mkdir data_distro/temp_data/')
    for file in load_file_names:
        # 30000 works
        for i, chunk in enumerate(read_csv("data_distro/data_to_load/{}".format(file), chunksize=35000, sep="|", encoding="mac-roman")):
            new_name = 'data_distro/temp_data/{0}-{1}.csv'.format(file, i)
            chunk.to_csv(new_name, index=False)
            temp_files.append(new_name)
    return temp_files

# Special conversions
boolean_conversion = {"Y":True, "N":False}

# Load files into django models
def load_files(temp_files):


# agency22.txt works

# for file_path in temp_files:
for f in load_file_names:
    file_path = "data_distro/data_to_load/{}".format(f)
    data_to_load = []
    # with open(file_path, newline="", encoding="mac-roman") as csvfile:
    # for loading FY 22
    file_name = file_path.replace("data_distro/data_to_load/", "")
    # table = re.sub("22.txt-\d+.csv", "", file_name)
    table = re.sub("22.txt", "", file_name)
    print("-----", table)
    print("Starting {0}...".format(file_name))
    fac_model_name = table_mappings[table]
    fac_model = getattr(mods, fac_model_name)
    # reader = read_csv(file_path, sep="|", encoding="mac-roman")
    for i, chunk in enumerate(read_csv(file_path, chunksize=35000, sep="|", encoding="mac-roman")):
        csv_dict = chunk.to_dict(orient='records')
        # read_csv("data_distro/data_to_load/{}".format(file), sep="|", encoding="mac-roman")
        # reader = csv.DictReader(csvfile)
        for row in csv_dict:
            # try:
            fields = list(row.keys())
            instance_dict = {}
            # should do this with the header instead
            for key in fields:
                field_name = field_mappings[key]
                payload = row[key]
                # break cleaning logic into a separate function
                print(field_name)
                if field_name in boolen_fields:
                    payload = boolean_conversion.get(payload, None)
                instance_dict[field_name] = payload
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
     3) Break up files into manageable chunks
     4) Load data into Django models
     ) Clean up temp files
    """
    all_file_names = next(walk("data_distro/data_to_load"), (None, None, []))[2]
    load_file_names = file_clean(all_file_names)
    temp_files = nomalize_csvs(load_file_names)
    load_files(temp_files)
    system('rm -rf data_distro/temp_data/')

load_data()
