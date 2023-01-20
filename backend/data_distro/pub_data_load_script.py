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
)

# Grab just the files we want, no ds_store etc
def file_clean(all_file_names):
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
        for i, chunk in enumerate(read_csv("data_distro/data_to_load/{}".format(file), chunksize=20000, sep="|", encoding="mac-roman")):
            new_name = 'data_distro/temp_data/{0}-{1}.csv'.format(file, i)
            chunk.to_csv(new_name, index=False)
            temp_files.append(new_name)
    return temp_files

# Load files into django models
def load_files(temp_files):
    for file_path in temp_files:
        data_to_load = []
        with open(file_path, newline="", encoding="mac-roman") as csvfile:
            # for loading FY 22
            file_name = file_path.replace("data_distro/temp_data/", "")
            table = re.sub("22.txt-\d+.csv", "", file_name)
            print("Starting {0}...".format(file_name))
            fac_model_name = table_mapping[table.lower()]
            reader = csv.DictReader(csvfile)
            try:
                for row in reader:
                    fields = list(row.keys())
                    data = ""
                    for key in fields:
                        data += "{0}={1},".format(field_mappings[key], row[key])
                    fac_model = getattr(mods, fac_model_name)
                    p = fac_model(data)
                    # p.save()
            except Exception:
                print("---------------------PROBLEM---------------------")
                traceback.print_exc()
                print(table)
                print(row)
                print("-------------------------------------------------")
            print("Finished {0}".format(file_name))

def load_data():
    """
     1) Find all the files for upload
     2) Create list of files we need
     3) Grab just the files we want
     4) Break up files into manageable chunks
     5) Load data into Django models
     6) Clean up temp files
    """
    all_file_names = next(walk("data_distro/data_to_load"), (None, None, []))[2]
    table_names = list(table_mappings.keys())
    load_file_names = file_clean(all_file_names)
    temp_files = nomalize_csvs(load_file_names)
    load_files(temp_files)
    system('rm -rf data_distro/temp_data/')

load_data()
