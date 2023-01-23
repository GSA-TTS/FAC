"""
Download data from https://facdissem.census.gov/PublicDataDownloads.aspx
Then unzip the files and place the them in data_distro/data_to_load/

Load them with: manage.py public_data_loader
"""
import csv
import re
from os import walk, system
import traceback
from pandas import read_csv
import logging
from dateutil import parser

from django.core.management.base import BaseCommand

from data_distro import models as mods
from data_distro.download_model_dictonaries import (
    model_title_transforms,
    field_transforms,
    table_mappings,
    field_mappings,
    boolen_fields,
)

logger = logging.getLogger(__name__)


def file_clean(all_file_names):
    """Grab just the files we want, no ds_store etc"""
    table_names = list(table_mappings.keys())
    file_names = []

    for f in all_file_names:
        # I am starting with loading from the FY 22 downloads
        name = f.replace("22.txt", "")
        if name in table_names:
            file_names.append(f)

    return file_names


def rename_headers(df):
    """Replaces headers with new field names that match the models"""
    headers_list = df.columns
    new_headers = []

    for header in headers_list:
        new_headers.append(field_mappings[header])

    df.columns = new_headers
    return df


def data_transform(field_name, payload):
    """Some fileld data needs to be altered in order to load it"""
    if field_name in boolen_fields:
        boolean_conversion = {"Y": True, "N": False}
        payload = boolean_conversion.get(payload, None)
    # CfdaInfo
    if field_name == "cfda":
        payload = str(payload)
    # CfdaInfo, auditee_fax is General
    if (
        field_name
        in [
            "cluster_total",
            "cpa_fax",
            "auditee_fax",
            "cognizant_agency",
            "ein_subcode",
        ]
        and str(payload) == "nan"
    ):
        payload = None
    # Dates are only in the gen table
    if "date" in field_name:
        if str(payload) == "nan":
            payload = None
        else:
            payload = parser.parse(payload)
    # These should be integers, but Pandas can think they are floats
    if field_name == "cognizant_agency":
        if type(payload) is float:
            if payload.is_integer():
                payload = str(int(payload))

    # trying this our on just General
    if str(payload) == "nan":
        payload = None

    #     #debug which column is triggering an int out of range error
    # if type(payload) == int:
    #     if payload > 2147483647:
    #         print("PROBLEM int~~~~~~~~~~~~~~~", field_name, payload)
    # if type(payload) == int:
    #     if payload > 2147483647:
    #         print("PROBLEM float~~~~~~~~~~~~~", field_name, payload)

    return payload


def handle_exceptions(
    table, file_path, instance_dict, fac_model_name, error_trace, exceptions_list
):
    """Add detailed explanations to the logs and keep track of each type of error"""
    logger.warn(
        """
        ---------------------PROBLEM---------------------
        {table}, {file_path}
        ----
        {instance_dict}
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        {trace}
        -------------------------------------------------
        """.format(
            table=table,
            file_path=file_path,
            instance_dict=instance_dict,
            trace=error_trace,
        )
    )
    problem_text = "Error loading {file_path} into {fac_model_name}: \n \
        {trace}".format(
        file_path=file_path,
        fac_model_name=fac_model_name,
        instance_dict=instance_dict,
        trace=error_trace,
    )
    if problem_text not in exceptions_list:
        exceptions_list.append(problem_text)


def load_files(load_file_names):
    """Load files into django models"""
    exceptions_list = []
    exceptions_count = 0

    for f in load_file_names:
        file_path = "data_distro/data_to_load/{}".format(f)
        file_name = file_path.replace("data_distro/data_to_load/", "")
        table = re.sub("22.txt", "", file_name)
        fac_model_name = table_mappings[table]
        fac_model = getattr(mods, fac_model_name)
        logger.warn(
            "Starting to load {0} into {1}...".format(file_name, fac_model_name)
        )

        for i, chunk in enumerate(
            read_csv(file_path, chunksize=35000, sep="|", encoding="mac-roman")
        ):
            chunk_with_headers = rename_headers(chunk)
            csv_dict = chunk_with_headers.to_dict(orient="records")

            for row in csv_dict:
                try:
                    fields = list(row.keys())
                    instance_dict = {}
                    for field_name in fields:
                        instance_dict[field_name] = data_transform(
                            field_name, row[field_name]
                        )
                    p, created = fac_model.objects.get_or_create(**instance_dict)

                except Exception:
                    handle_exceptions(
                        table,
                        file_path,
                        instance_dict,
                        fac_model_name,
                        traceback.format_exc(),
                        exceptions_list,
                    )
                    exceptions_count += 1

            logger.warn("finished chunk")
        logger.warn("Finished {0}".format(file_name))
        return exceptions_list, exceptions_count


class Command(BaseCommand):
    help = """
        Loads data from public download files into Django models. It will automatically \
        crawl "/backend/data_distro/data_to_load". \
        If you just want one file, you can pass the name of the file with -p.
    """

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", type=str, help="file name")

    def handle(self, *args, **kwargs):
        """
        1) Find the files for upload
        2) Grab just the files we want
        3) Load data into Django models
        """
        if kwargs["file"] is not None:
            load_file_names = [kwargs["file"]]
        else:
            file_names = next(walk("data_distro/data_to_load"), (None, None, []))[2]
            load_file_names = file_clean(file_names)

        errors, exceptions_count = load_files(load_file_names)

        if exceptions_count > 0:
            message = """###############################
                {0} error types in {1} records:
                ###############################""".format(
                len(errors), exceptions_count
            )
            for err in errors:
                message += """
                {0}
                """.format(
                    err
                )
            logger.error(message)
        else:
            logger.warn("Successful upload")
