"""
Functions that the public data loader uses to process and transform data.
These functions look at one row of data at a time and save results.
"""
import traceback
from dateutil import parser

from django.apps import apps
from data_distro.mappings.upload_mapping import upload_mapping
from data_distro.mappings.upload_dictonaries import boolen_fields

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
    if field_name in boolen_fields:
        boolean_conversion = {"Y": True, "N": False}
        return boolean_conversion.get(payload, None)
    if str(payload) == "nan":
        return None
    # CfdaInfo
    if field_name == "cfda":
        return str(payload)
    # Dates are only in the gen table
    if "date" in field_name:
        return parser.parse(payload)
    # These should be integers, but Pandas can think they are floats
    if field_name == "cognizant_agency":
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
        if model_name == "Auditee":
            # easier if these exist so that we can just append when we add them, we might want to replace empty lists with nulls after all data is loaded
            instances_dict[model_name]["duns_list"] = []
            instances_dict[model_name]["uei_list"] = []

    return instances_dict


def transform_and_save(
    row,
    csv_dict,
    table,
    file_path,
    exceptions_list,
):
    """
    For each row in the download, it looks at the data element and skips, or passes on  the data for cleaning.
    Then, it adds metadata and calls the save function for the created objects.
    """
    model_dict = create_model_dict()
    try:
        columns = [str(key) for key in row]
        instances_dict = {}
        for column in columns:
            instances_dict = transform_payload(row, table, column, instances_dict)

            # save each model instance
            objects_dict = {}

        for model_name in instances_dict.keys():
            fac_model = model_dict[model_name]
            instances_dict = add_metadata(instances_dict, model_name)
            p, created = fac_model.objects.get_or_create(**instances_dict[model_name])

            objects_dict[model_name] = p

        return objects_dict, exceptions_list

    except Exception:
        exceptions_list = handle_exceptions(
            table,
            file_path,
            instances_dict,
            traceback.format_exc(),
            exceptions_list,
        )

        return None, exceptions_list


def transform_and_save_w_exceptions(
    row,
    csv_dict,
    table,
    file_path,
    exceptions_list,
):
    """
    For each row in the download, it looks at the data element and skips, or passes on  the data for cleaning.
    Then, it adds metadata and calls the save function for the created objects.

    This has additional checks and links relevant for loading the general table.
    """
    model_dict = create_model_dict()
    try:
        columns = [str(key) for key in row]
        instances_dict = {}
        # skip fields only for general
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
        for column in columns:
            mapping = table + column
            if mapping not in skip_list:
                instances_dict = transform_payload(row, table, column, instances_dict)

        # save each model instance
        objects_dict = {}
        for model_name in instances_dict.keys():
            instances_dict = add_metadata_general(instances_dict, model_name)
            fac_model = model_dict[model_name]
            p, created = fac_model.objects.get_or_create(**instances_dict[model_name])

            objects_dict[model_name] = p

        return (
            objects_dict,
            exceptions_list,
        )

    except Exception:
        (exceptions_list,) = handle_exceptions(
            table,
            file_path,
            instances_dict,
            traceback.format_exc(),
            exceptions_list,
        )

        return (
            None,
            exceptions_list,
        )
