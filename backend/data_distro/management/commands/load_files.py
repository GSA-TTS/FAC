import csv

from pandas import read_csv
import logging

from data_distro.management.commands.process_data import (
    transform_and_save,
    transform_and_save_w_exceptions,
)
from data_distro.management.commands.handle_errors import handle_badlines
from data_distro.models import General
from data_distro.management.commands.link_data import (
    link_objects_findings,
    link_objects_cpas,
    link_objects_general,
)


logger = logging.getLogger(__name__)


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
    expected_objects_dict = {}

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
            read_csv(
                file_path,
                chunksize=30000,
                sep="|",
                encoding="mac-roman",
                on_bad_lines=handle_badlines,
                engine="python",
                quoting=csv.QUOTE_NONE,
            )
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
                "finished {0} chunk - last row DBKEY {1}, objects count = {2}".format(
                    table, row["DBKEY"], expected_object_count
                )
            )
        expected_objects_dict[file_name] = expected_object_count
        logger.warning(
            f"Finished {file_name}, {expected_object_count} expected objects"
        )

    return exceptions_list, expected_objects_dict
