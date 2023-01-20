import csv
from os import walk

# from models.py import *
# from download_model_dictonaries import model_title_transforms, field_transforms
from data_distro.models import *
from data_distro.download_model_dictonaries import (
    model_title_transforms,
    field_transforms,
)

all_file_names = next(walk("data_distro/data"), (None, None, []))[2]


table_names = []
table_mapping = {}
for title in model_title_transforms:
    for key in title:
        table_names.append(key)
        table_mapping[key] = title[key]

field_mappings = {}
for f in field_transforms:
    for key in f:
        field_mappings[key] = f[key]

file_names = []


def file_clean(all_file_names):
    for f in all_file_names:
        # I am starting with loading from the FY 22 downloads
        name = f.replace("22.txt", "")
        if name in table_names:
            file_names.append(f)
    return file_names


load_file_names = file_clean(all_file_names)

for file_name in load_file_names:
    file_path = "data_distro/data/{0}".format(file_name)
    data_to_load = []
    with open(file_path, newline="") as csvfile:
        # for loading FY 22
        x = file_name.replace("22.txt", "")
        fac_model_name = table_mapping[x]
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            # left off here
            # for data in row:
            #     element = field_transforms[header_row[postion]
            #     row += "{}={},".format(element, data)
            #     postion += 1
            # fac_model = getattr(models.py, fac_model_name)
            # p = fac_model(row)
            # p.save()
