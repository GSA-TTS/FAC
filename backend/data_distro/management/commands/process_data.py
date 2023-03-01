"""
Functions that the public data loader uses to process and transform data.
These functions look at one row of data at a time and save results.
"""
import re
import traceback
from dateutil import parser  # type: ignore

from django.apps import apps

from data_distro.mappings.upload_mapping import upload_mapping
from data_distro.mappings.upload_dictonaries import boolean_fields
from data_distro.management.commands.handle_errors import handle_exceptions


def create_model_dict():
    """creates {"model_name": < model_object >}"""
    model_dict = {}
    distro_classes = apps.all_models["data_distro"]

    for model in distro_classes:
        mod_class = distro_classes[model]
        mod_name = mod_class.__name__
        model_dict[mod_name] = mod_class

    return model_dict


def data_transform(field_name, payload):
    """Some fileld data needs to be altered in order to load it"""
    if field_name in boolean_fields:
        boolean_conversion = {"Y": True, "N": False}
        return boolean_conversion.get(payload, None)
    # This is how pandas represents nulls
    elif str(payload) == "nan":
        return None
    # Dates are only in the gen table
    elif "date" in field_name:
        return parser.parse(payload)
    # Gets rid of some stray characters
    elif "phone" in field_name or "fax" in field_name:
        payload = int(re.sub("[^0-9]", "", str(payload)))
    # Some of these were getting converted to decimals
    elif field_name == "dbkey":
        payload = str(int(payload))
    # These should be integers, but Pandas can think they are floats
    elif field_name == "cognizant_agency" or field_name == "cfda":
        if type(payload) is float:
            if payload.is_integer():
                payload = str(int(payload))

    # ## debug which column is triggering an int out of range error
    # if type(payload) == int:
    #     if payload > 2147483647:
    #         logger.warn("PROBLEM int~~~~~~~~~~~~~~~", field_name, payload)
    # if type(payload) == int:
    #     if payload > 2147483647:
    #         logger.warn("PROBLEM float~~~~~~~~~~~~~", field_name, payload)

    return payload


def transform_payload(row, table, column, instances_dict):
    """Map out new names from the download names"""
    model_name = upload_mapping[table][column][0]
    field_name = upload_mapping[table][column][1]
    field_data = row[column]

    payload = data_transform(field_name, field_data)

    if model_name in instances_dict.keys():
        instances_dict[model_name][field_name] = payload
    else:
        instances_dict[model_name] = {}
        instances_dict[model_name][field_name] = payload

    return instances_dict


def add_metadata(instances_dict, model_name):
    """Adding a data source and prepping the list fields"""
    for model_name in instances_dict.keys():
        instances_dict[model_name]["is_public"] = True

    return instances_dict


def add_metadata_general(instances_dict, model_name):
    """Add relevant metadata for what we extract from the General table"""
    for model_name in instances_dict.keys():
        instances_dict[model_name]["is_public"] = True
        if model_name == "General":
            instances_dict[model_name]["data_source"] = "public downloads"

    return instances_dict


def create_instances_dict(row, table):
    """
    Save the data in the row as data ready for model instances and create a dictionary of the new instances. (For simple tables.)
    sample objects_dict structure {"gen": {id: "x", name: "y"}, 'auditee': {id: "x", name: "y"}}
    """
    columns = [str(key) for key in row]
    instances_dict = {}

    for column in columns:
        instances_dict = transform_payload(row, table, column, instances_dict)

    return instances_dict


def create_instances_dict_w_exceptions(row, table, skip_list):
    """
    Save the data in the row as data ready for model instances and create a dictionary of the new instances. (For tables that have a lot of exceptions to the rules)
    sample objects_dict structure {"gen": {id: "x", name: "y"}, 'auditee': {id: "x", name: "y"}}
    """
    columns = [str(key) for key in row]
    instances_dict = {}

    for column in columns:
        mapping = table + column
        if mapping not in skip_list:
            instances_dict = transform_payload(row, table, column, instances_dict)
        elif mapping == "genDUNS":
            instances_dict.setdefault("Auditee", {})
            if str(row["DUNS"]) == "nan":
                instances_dict["Auditee"]["duns_list"] = []
            else:
                instances_dict["Auditee"]["duns_list"] = [int(row["DUNS"])]
        elif mapping == "genEIN":
            instances_dict.setdefault("Auditee", {})
            if str(row["EIN"]) == "nan":
                instances_dict["Auditee"]["ein_list"] = []
            else:
                instances_dict["Auditee"]["ein_list"] = [int(row["EIN"])]
        elif mapping == "genUEI":
            instances_dict.setdefault("Auditee", {})
            if str(row["UEI"]) == "nan":
                instances_dict["Auditee"]["uei_list"] = []
            else:
                instances_dict["Auditee"]["uei_list"] = [int(row["UEI"])]

    return instances_dict


def create_objects_dict(instances_dict):
    """
    Save the data in the row as a model instances and create a dictionary of the new instances.
    sample objects_dict structure {"gen": <gen_instance>, 'auditee': <auditee_instance>}
    """
    objects_dict = {}
    model_dict = create_model_dict()

    for model_name in instances_dict:
        fac_model = model_dict[model_name]
        instances_dict = add_metadata(instances_dict, model_name)
        new_instance, _created = fac_model.objects.get_or_create(
            **instances_dict[model_name]
        )

        objects_dict[model_name] = new_instance

    return objects_dict


def transform_and_save(
    row,
    csv_dict,
    table,
    file_path,
):
    """
    For each row in the download, it looks at the data element and skips, or passes on  the data for cleaning.
    Then, it adds metadata and calls the save function for the created objects.
    """
    try:
        instances_dict = create_instances_dict(row, table)
        objects_dict = create_objects_dict(instances_dict)
        return objects_dict

    except Exception:
        handle_exceptions(
            str(table),
            str(file_path),
            instances_dict,
            traceback.format_exc(),
        )
        return None


def transform_and_save_w_exceptions(
    row,
    csv_dict,
    table,
    file_path,
):
    """
    For each row in the download, it looks at the data element and skips, or passes on  the data for cleaning.
    Then, it adds metadata and calls the save function for the created objects.

    This function has additional checks and links relevant for loading the gen and cpas tables.
    """
    model_dict = create_model_dict()
    try:
        # These fields are not processed with the transform_payload function
        skip_list = [
            # removed
            "genMULTIPLEEINS",
            "genMULTIPLEDUNS",
            "genMULTIPLE_CPAS",
            "genMULTIPLEUEIS",
            # stored in 2 places
            "genAUDITOR_EIN",
            # processed later
            "genDUNS",
            "genEIN",
            "genUEI",
            "cpasAUDITYEAR",
            "cpasDBKEY",
        ]

        instances_dict = create_instances_dict_w_exceptions(row, table, skip_list)

        # Save each model instance from the instances_dict
        objects_dict = {}
        for model_name in instances_dict:
            instances_dict = add_metadata_general(instances_dict, model_name)
            fac_model = model_dict[model_name]
            new_instance, _created = fac_model.objects.get_or_create(
                **instances_dict[model_name]
            )

            objects_dict[model_name] = new_instance

        return objects_dict

    except Exception:
        handle_exceptions(
            str(table),
            str(file_path),
            instances_dict,
            traceback.format_exc(),
        )

        return None
