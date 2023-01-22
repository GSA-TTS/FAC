"""
Download data from https://facdissem.census.gov/PublicDataDownloads.aspx
Then unzip the files and place the them in data_distro/data_to_load/
"""
import csv
import re
from os import walk, system
import traceback
from pandas import read_csv
import logging

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

# Special conversions
boolean_conversion = {"Y":True, "N":False}

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


def load_files(load_file_names):
    """Load files into django models"""
    print
    for f in load_file_names:
        file_path = "data_distro/data_to_load/{}".format(f)
        file_name = file_path.replace("data_distro/data_to_load/", "")
        table = re.sub("22.txt", "", file_name)
        fac_model_name = table_mappings[table]
        fac_model = getattr(mods, fac_model_name)
        logger.warn("Starting to load {0} into {1}...".format(file_name, fac_model_name))
        
        for i, chunk in enumerate(read_csv(file_path, chunksize=35000, sep="|", encoding="mac-roman")):
            csv_dict = chunk.to_dict(orient='records')
            for row in csv_dict:
                try:
                    fields = list(row.keys())
                    instance_dict = {}
                    # should do this with the header instead
                    for key in fields:
                        field_name = field_mappings[key]
                        payload = row[key]
                        # break cleaning logic into a separate function
                        if field_name in boolen_fields:
                            payload = boolean_conversion.get(payload, None)
                        # CfdaInfo
                        if field_name == "cfda":
                            payload = str(payload)
                        # CfdaInfo
                        if field_name in ["cluster_total", "cpa_fax"] and payload == 'nan':
                            payload == None
                        instance_dict[field_name] = payload
                    p, created = fac_model.objects.get_or_create(**instance_dict)

                except Exception:
                    logger.warn("""
                        ---------------------PROBLEM---------------------
                        {table}, {file_path}
                        ----
                        {instance_dict}
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        {trace}
                        -------------------------------------------------
                        """.format(
                            table = table,
                            file_path = file_path,
                            instance_dict = instance_dict,
                            trace = traceback.print_exc(),
                        )
                    )
            print("finished chunk")
        print("Finished {0}".format(file_name))

class Command(BaseCommand):
    help = """
        Loads data from public download files into Django models. It will automatically \
        crawl "/backend/data_distro/data_to_load". \
        If you just want one file, you can pass the name of the file with -p.
    """

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', type=str, help='file name')

    def handle(self, *args, **kwargs):
        """
         1) Find the files for upload
         2) Grab just the files we want
         3) Load data into Django models
        """
        if kwargs['file'] is not None:
            load_file_names = [ kwargs['file'] ]
        else:
            file_names = next(walk("data_distro/data_to_load"), (None, None, []))[2]
            load_file_names = file_clean(file_names)

        load_files(load_file_names)
