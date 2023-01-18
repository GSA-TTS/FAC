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
    """
    I ran this locally to create the structure:
    {
        model_1: {
            field_name1: [desc, field_type],
            field_name2: [desc, field_type],
        },
        model_2: {
            field_name3: [desc, field_type],
        }
    }
    """
    line = d.split("|")
    model = make_model_name(line[0])
    if model not in model_dict:
        model_dict[model] = {}
    model_dict[model][make_field_name(line[1])] = [line[2].strip(), line[3].strip()]
