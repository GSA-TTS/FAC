# Doing this in console for a one-time data grab and mapping using the data download key.
# Then, I can use the mappings to evolve the import script.

from pandas import read_csv

from data_distro.download_model_dictonaries import (
    table_mappings_from_key,
    field_mappings,
)
from data_distro.v1_crosswalk_for_docs import doc_metadata

""" getting docs """
# detailed description generator
data_key = read_csv(
    "data_distro/data_to_load/DataDownloadKey.csv", encoding="mac-roman"
)
data_dict = data_key.to_dict(orient="records")


# want to create
sample_data = {
    new_name: {
        "models": ["Model1", "Model2"],
        "original_name": "ORIGINALNAME",
        "descriptions": ["description1", "description2"],
        "description_model1": "description1",
        "description_model2": "description2",
        "forms": ["SAC 1997-200, line 32", "SF-SAC 2022, line 7"],
        "forms_modlel1": ["SAC 1997-200, line 32", "SF-SAC 2022, line 7"],
        "forms_modlel2": ["SAC 1997-200, line 32", "SF-SAC 2022, line 7"],
        "all_years": False,
    }
}

doc_metadata = {}

for field_data in data_dict.keys():
    row = doc_metadata[field_data]
    new_name = field_data
    new_model = table_mappings_from_key[row["TABLE"]]
    forms_per_model = "forms_{0}".format(new_model)
    if new_name not in doc_metadata:
        doc_metadata[new_name] = {}
        d = doc_metadata[new_name]
        d["models"] = [new_model]
        d["original_name"] = row["FIELD NAME"]
        # populate values below
        d["forms"] = []
        d[forms_per_model] = []
        d["descriptions"] = []
    else:
        d = doc_metadata[new_name]
        d["models"].append(new_model)
        d[forms_per_model] = []
    for header in row.keys():
        value = row[header]
        # float catches the nans
        if header.startswith("SF-SAC") and type(value) != float:
            form_location = "{}: {}".format(header, value)
            d["forms"].append(form_location)
            d[forms_per_model].append(form_location)
    d["descriptions"].append(row["DESCRIPTION"])
    d["description_{0}".format(new_model)] = row["DESCRIPTION"]
    d["original_table_{0}".format(new_model)] = row["TABLE"]
    # If I need to check if something can be null later
    if len(d["descriptions"]) < 9:
        d["all_years"] = True
    if len(d["descriptions"]) == 9:
        d["all_years"] = False

"""Use doc metadata to generate doc string documentation"""

for field in doc_metadata.keys():
    for model in doc_metadata[field]["models"]:
        data = doc_metadata[field]
        table_key = "original_table_{}".format(model)
        table = data[table_key],
        original_name = data["original_name"],
        if len(data["models"]) > 1:
            differentiator = "_{0}".format(model.lower())
        else:
            differentiator = ""
        if len(data["forms_{}".format(model)]) > 0:
            form_list = data["forms_{}".format(model)]
            form_text = ";".join(form_list)
            sources = "Data sources: {0} ".format(form_text)
        else:
            sources = ""
        docstring = '{field_name}{differentiator}_doc = "{sources}Census mapping: {table}, {original_name}"'.format(
            field_name=field,
            differentiator=differentiator,
            sources=sources,
            table=table,
            original_name=original_name,
        )
        print(docstring)

"""first pass at making models from the download key"""

field_transforms = []
model_transforms = []
model_dict = {}


def make_model_name(table_name):
    """make a key to transform names of tables to models"""
    name = table_name.title()
    name = name.replace(" ", "")
    if {table_name.strip(): name} not in model_transforms:
        model_transforms.append({table_name.strip(): name})
    return name


def make_field_name(field_name):
    """make a key to transform names of column name to field names"""
    name = field_name.replace(" ", "").lower()
    if {field_name.strip(): name} not in field_transforms:
        field_transforms.append({field_name.strip(): name})
    return name


for d in data.split("\n"):
    line = d.split("|")
    model = make_model_name(line[0])
    if model not in model_dict:
        model_dict[model] = {}
    model_dict[model][make_field_name(line[1])] = [
        line[2].strip(),
        line[3].strip(),
        line[4],
    ]


# create model text, just printing to console
for model in model_dict:
    print("class {model}(models.Model):".format(model=model))
    for element_key in model_dict[model]:
        print(
            """    {field_name} = models.{field_type}("{description}", {validation})""".format(
                field_name=element_key,
                field_type=model_dict[model][element_key][1],
                description=model_dict[model][element_key][0],
                validation=model_dict[model][element_key][2].strip(),
            )
        )
    print("\n")
