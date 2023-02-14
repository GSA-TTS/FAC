"""
Download data from https://facdissem.census.gov/PublicDataDownloads.aspx
Then unzip the files and place the them in data_distro/data_to_load/

Load them with: manage.py public_data_loader
"""
from pandas import read_csv
import logging

from django.core.management.base import BaseCommand

from data_distro.management.commands.process_data import (
    transform_and_save,
    transform_and_save_w_exceptions,
)
from data_distro.management.commands.handle_errors import log_results
from data_distro.models import General
from data_distro.management.commands.link_data import (
    link_objects_findings,
    link_objects_cpas,
    link_objects_general,
    add_duns_eins,
    add_agency,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
        Loads data from public download files into Django models. Add the data to "/backend/data_distro/data_to_load". \
        If you just want one file, you can pass the name of the file with -f.

        Requires pandas.

        See docs/data_loaing.md for more details.
    """

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", type=str, help="file name")
        parser.add_argument("-y", "--year", type=str, help="Two digit year of downloads, as they appear in the file names. Leave blank for all years. Not needed if using file name kwarg.")

    def handle(self, *args, **kwargs):
        """
        1) Find the files for upload
        2) Grab just the files we want
        3) Load data into Django models
        4) Add DUNS relationships
        """
        if kwargs["file"] is not None:
            load_file_names = [kwargs["file"]]
            if "duns" in load_file_names or "ein" in load_file_names:
                add_duns_eins(load_file_names)
            elif "agency" in load_file_names:
                add_agency(load_file_names)
            else:
                exceptions_list = load_files(load_file_names)

        else:
            year = kwargs["year"]
            if year == None:
                year = ""

            # Dependent objects are created first
            load_file_names = [
                f"findingstext_formatted{year}.txt",
                f"findings{year}.txt",
                f"captext_formatted{year}.txt",
                f"cfda{year}.txt",
                f"notes{year}.txt",
                f"revisions{year}.txt",
                f"passthrough{year}.txt",
                f"gen{year}.txt",
                f"cpas{year}.txt",
            ]

            exceptions_list = load_files(load_file_names)
            # doing manually for this pass
            add_duns_eins(f"duns{year}.txt")
            add_duns_eins(f"eins{year}.txt")
            add_agency(f"agency{year}.txt")

        log_results(exceptions_list)


def load_generic(
    row,
    csv_dict,
    table,
    file_path,
    exceptions_list,
):

    objects_dict, exceptions_list, = transform_and_save(
        row,
        csv_dict,
        table,
        file_path,
        exceptions_list,
    )
    if table == "findings":
        link_objects_findings(objects_dict)

    return exceptions_list


def load_cpas(
    row,
    csv_dict,
    table,
    file_path,
    exceptions_list,
):
    objects_dict, exceptions_list, = transform_and_save_w_exceptions(
        row,
        csv_dict,
        table,
        file_path,
        exceptions_list,
    )
    link_objects_cpas(objects_dict, row)

    return exceptions_list


def load_general(
    row,
    csv_dict,
    table,
    file_path,
    exceptions_list,
):
    # Since we can add additional information later, like additional eins, agencies, and auditors, we don't want to do a find or create call on this data. I am adding an upfront check.
    try:
        General.objects.get(dbkey=row["DBKEY"], audit_year=row["AUDITYEAR"])
        loaded = True
    except General.DoesNotExist:
        loaded = False

    if loaded is False:
        for row in csv_dict:
            objects_dict, exceptions_list = transform_and_save_w_exceptions(
                row,
                csv_dict,
                "gen",
                file_path,
                exceptions_list,
            )

            link_objects_general(objects_dict)

    return exceptions_list


def load_files(load_file_names):
    """Load files into django models"""

    for file in load_file_names:
        exceptions_list = []
        file_path = f"data_distro/data_to_load/{file}"
        file_name = file_path.replace("data_distro/data_to_load/", "")
        # Remove numbers, there are years in the file names, remove file extension
        table = "".join([i for i in file_name if not i.isdigit()])[:-4]
        # Remove for testing
        table = table.replace("test_data/", "")
        logger.warning(f"Starting to load {file_name}...")
        expected_object_count = 0


        for i, chunk in enumerate(
            read_csv(file_path, chunksize=35000, sep="|", encoding="mac-roman")
        ):
            csv_dict = chunk.to_dict(orient="records")
            expected_object_count += len(csv_dict)

            # Just to speed things up check things per table and not per row or element
            logger.warning(f"------------Table: {table}--------------")
            if table not in ["gen", "general", "cpas"]:
                for row in csv_dict:
                    exceptions_list = load_generic(
                        row,
                        csv_dict,
                        table,
                        file_path,
                        exceptions_list,
                    )
            elif table == "cpas":
                for row in csv_dict:
                    exceptions_list = load_cpas(
                        row,
                        csv_dict,
                        table,
                        file_path,
                        exceptions_list,
                    )
            else:
                # Some years the table is called gen and sometimes general
                for row in csv_dict:
                    exceptions_list = load_general(
                        row,
                        csv_dict,
                        "gen",
                        file_path,
                        exceptions_list,
                    )

            logger.warning(
                "finished chunk - last row {0}, objects count = {1}".format(
                    row["DBKEY"], expected_object_count
                )
            )
        logger.warning(f"Finished {file_name}, {expected_object_count} expected objects")

    return exceptions_list
