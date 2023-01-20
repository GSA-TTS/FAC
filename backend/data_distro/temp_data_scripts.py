# Doing this in console for a one-time data grab and mapping using the data download key.
# Then, I can use the mappings to evolve the import script.
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
