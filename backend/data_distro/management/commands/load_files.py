from pandas import read_csv
import logging

from data_distro.management.commands.process_data import (
    transform_and_save,
    transform_and_save_w_exceptions,
)
from data_distro.models import General
from data_distro.management.commands.link_data import (
    link_objects_findings,
    link_objects_cpas,
    link_objects_general,
    link_duns_eins,
    link_agency,
)
from data_distro.management.commands.parse_config import (
    panda_config,
    panda_config_formatted,
    panda_config_base,
)


logger = logging.getLogger(__name__)


def load_generic(
    row,
    csv_dict,
    table,
    file_path,
):

    objects_dict = transform_and_save(
        row,
        csv_dict,
        table,
        file_path,
    )
    if table == "findings":
        link_objects_findings(objects_dict)


def load_cpas(
    row,
    csv_dict,
    table,
    file_path,
):
    objects_dict = transform_and_save_w_exceptions(
        row,
        csv_dict,
        table,
        file_path,
    )
    link_objects_cpas(objects_dict, row)


def load_general(
    row,
    csv_dict,
    table,
    file_path,
):
    # Since we can add additional information later, like additional eins, agencies, and auditors, we don't want to do a find or create call on this data. I am adding an upfront check.
    try:
        General.objects.get(dbkey=row["DBKEY"], audit_year=row["AUDITYEAR"])
        loaded = True
    except General.DoesNotExist:
        loaded = False

    if loaded is False:
        for row in csv_dict:
            objects_dict = transform_and_save_w_exceptions(
                row,
                csv_dict,
                "gen",
                file_path,
            )

            link_objects_general(objects_dict)


def load_files(load_file_names):
    """Load files into django models"""
    expected_objects_dict = {}

    for file in load_file_names:
        file_path = f"data_distro/data_to_load/{file}"
        file_name = file_path.replace("data_distro/data_to_load/", "")
        # Remove numbers, there are years in the file names, remove file extension
        table = "".join([i for i in file_name if not i.isdigit()])[:-4]
        # Remove for testing
        table = table.replace("test_data/", "")
        logger.warning(f"Starting to load {file_name}...")
        expected_object_count = 0

        if "formatted" in file_path:
            # These need a quote char
            config = panda_config_formatted
        else:
            # These do better ignoring the quote char
            config = panda_config

        for i, chunk in enumerate(read_csv(file_path, **config)):
            csv_dict = chunk.to_dict(orient="records")
            expected_object_count += len(csv_dict)

            # Just to speed things up check things per table and not per row or element
            logger.warning(f"------------Table: {table}--------------")
            if table not in ["gen", "general", "cpas"]:
                for row in csv_dict:
                    load_generic(
                        row,
                        csv_dict,
                        table,
                        file_path,
                    )
            elif table == "cpas":
                for row in csv_dict:
                    load_cpas(
                        row,
                        csv_dict,
                        table,
                        file_path,
                    )
            else:
                # Some years the table is called gen and sometimes general
                for row in csv_dict:
                    load_general(
                        row,
                        csv_dict,
                        "gen",
                        file_path,
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

    return expected_objects_dict


def load_duns_eins(file):
    """
    These were their own data model but we are going to use an array field.
    This adds the fields in the right order. It should run after general.
    """
    file_path = f"data_distro/data_to_load/{file}"
    if "duns" in file:
        sort_by = "DUNSEQNUM"
        payload_name = "DUNS"
    else:
        sort_by = "EINSEQNUM"
        payload_name = "EIN"

    # Can't do chunks because we want to order the dataframe
    data_frame = read_csv(file_path, **panda_config_base)
    # This will make sure we load the lists in the right order
    data_frame = data_frame.sort_values(by=sort_by, na_position="first")
    csv_dict = data_frame.to_dict(orient="records")
    expected_object_count = len(csv_dict)

    link_duns_eins(csv_dict, payload_name)

    return expected_object_count


def load_agency(file_name):
    """
    De-duping agency and adding as relationships
    """
    file_path = f"data_distro/data_to_load/{file_name}"
    data_frame = read_csv(file_path, **panda_config_base)
    csv_dict = data_frame.to_dict(orient="records")
    expected_object_count = len(csv_dict)

    link_agency(csv_dict, file_name)

    return expected_object_count
