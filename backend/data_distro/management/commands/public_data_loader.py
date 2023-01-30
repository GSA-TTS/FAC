"""
Download data from https://facdissem.census.gov/PublicDataDownloads.aspx
Then unzip the files and place the them in data_distro/data_to_load/

Load them with: manage.py public_data_loader
"""
import traceback
from pandas import read_csv
import logging
from dateutil import parser

from django.apps import apps
from django.core.management.base import BaseCommand

from data_distro import models as mods
from data_distro.download_model_dictonaries import (
    table_mappings,
    boolen_fields,
)
from data_distro.upload_mapping import upload_mapping

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
        trace=error_trace,
    )
    if problem_text not in exceptions_list:
        exceptions_list.append(problem_text)


def create_model_dict():
    """creates {"model_name": < model_object >}"""
    model_dict = {}
    distro_classes = apps.all_models["data_distro"]

    for model in distro_classes:
        mod_class = distro_classes[model]
        mod_name = mod_class.__name__
        model_dict[mod_name] = mod_class

    return model_dict


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
    row, csv_dict, table, file_path, fac_model_name, exceptions_count, exceptions_list
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

        return objects_dict

    except Exception:
        handle_exceptions(
            table,
            file_path,
            instances_dict,
            fac_model_name,
            traceback.format_exc(),
            exceptions_list,
        )


def transform_and_save_w_exceptions(
    row, csv_dict, table, file_path, fac_model_name, exceptions_count, exceptions_list
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
            fac_model = model_dict[model_name]
            instances_dict = add_metadata_general(instances_dict, model_name)
            p, created = fac_model.objects.get_or_create(**instances_dict[model_name])

            objects_dict[model_name] = p

        return objects_dict

    except Exception:
        handle_exceptions(
            table,
            file_path,
            instances_dict,
            fac_model_name,
            traceback.format_exc(),
            exceptions_list,
        )


def link_objects_findings(objects_dict):
    """Adds relationships between finding and finding text"""
    instance = objects_dict["Findings"]
    dbkey = instance.dbkey
    audit_year = instance.audit_year
    findings_text = mods.FindingsText.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for finding_text in findings_text:
        instance.findings_text = finding_text
        instance.save()


def link_objects_cpas(objects_dict, row):
    """Adds relationships between the general table and auditors for the cpas table"""
    auditor_instance = objects_dict["Auditor"]
    dbkey = row["DBKEY"]
    audit_year = row["AUDITYEAR"]
    gen_instance = mods.General.objects.filter(dbkey=dbkey, audit_year=audit_year)[0]
    gen_instance.auditor.add(auditor_instance)
    gen_instance.save()


def link_objects_general(objects_dict):
    """Adds relationships between the General model and other models"""
    # General model instance
    instance = objects_dict["General"]
    dbkey = instance.dbkey
    audit_year = instance.audit_year

    # Models that link to general

    auditee = objects_dict["Auditee"]
    instance.auditee = auditee

    # there can be multiple but only one from the gen form, cpas run next
    auditors = mods.Auditor.objects.filter(id=objects_dict["Auditor"].id)
    instance.auditor.set(auditors)

    cfdas = mods.CfdaInfo.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for cfda in cfdas:
        instance.cfda = cfda

    findings = mods.Findings.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for finding in findings:
        instance.findings = finding

    cap_texts = mods.CapText.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for cap_text in cap_texts:
        instance.cap_text = cap_text

    notes = mods.Notes.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for note in notes:
        instance.notes = note

    revisions = mods.Revisions.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for revision in revisions:
        instance.revidions = revision

    passthroughs = mods.Passthrough.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for passthrough in passthroughs:
        instance.passthrough = passthrough

    agencies = mods.Agencies.objects.filter(dbkey=dbkey, audit_year=audit_year)
    instance.agency.set(agencies)

    instance.save()


def add_duns():
    """
    These were their own data model but we are going to use an array field.
    This adds the fields in the right order.
    """
    file_path = "data_distro/data_to_load/duns22.txt"

    # can't do chunks because we want to order the dataframe
    data_frame = read_csv(file_path, sep="|", encoding="mac-roman")
    # this will make sure we load the lists in the right order
    data_frame = data_frame.sort_values(by="DUNSEQNUM")
    csv_dict = data_frame.to_dict(orient="records")

    for row in csv_dict:
        dbkey = row["DBKEY"]
        audit_year = row["AUDITYEAR"]
        duns = row["DUNS"]
        general_instance = mods.General.objects.filter(
            dbkey=dbkey, audit_year=audit_year
        )[0]
        auditee_instance = general_instance.auditee
        duns_list = auditee_instance.duns_list
        if duns not in duns_list:
            duns_list.append(int(duns))
            auditee_instance.duns_list = duns_list
            auditee_instance.save()


def load_files(load_file_names):
    """Load files into django models"""
    exceptions_list = []
    exceptions_count = 0

    for file in load_file_names:
        file_path = "data_distro/data_to_load/{}".format(file)
        file_name = file_path.replace("data_distro/data_to_load/", "")
        # remove numbers, there are years in the file names, remove file extension
        table = "".join([i for i in file_name if not i.isdigit()])[:-4]
        fac_model_name = table_mappings[table]
        # fac_model = getattr(mods, fac_model_name)
        logger.warn("Starting to load {0}...".format(file_name))

        for i, chunk in enumerate(
            read_csv(file_path, chunksize=35000, sep="|", encoding="mac-roman")
        ):
            # chunk_with_headers = rename_headers(chunk)
            csv_dict = chunk.to_dict(orient="records")

            # just to speed things up check things per table and not per row or element
            logger.warn("------------Table: {0}--------------".format(table))
            if table != "gen" and table != "cpas":
                for row in csv_dict:
                    objects_dict = transform_and_save(
                        row,
                        csv_dict,
                        table,
                        file_path,
                        fac_model_name,
                        exceptions_count,
                        exceptions_list,
                    )
                    if table == "findings":
                        link_objects_findings(objects_dict)
            elif table == "cpas":
                for row in csv_dict:
                    objects_dict = transform_and_save_w_exceptions(
                        row,
                        csv_dict,
                        table,
                        file_path,
                        fac_model_name,
                        exceptions_count,
                        exceptions_list,
                    )
                    link_objects_cpas(objects_dict, row)
            else:
                for row in csv_dict:
                    objects_dict = transform_and_save_w_exceptions(
                        row,
                        csv_dict,
                        table,
                        file_path,
                        fac_model_name,
                        exceptions_count,
                        exceptions_list,
                    )
                    link_objects_general(objects_dict)

            logger.warn("finished chunk")
        logger.warn("Finished {0}".format(file_name))
    return exceptions_list, exceptions_count


def log_results(errors, exceptions_count):
    """This is helpful for debugging"""
    if exceptions_count > 0:
        message = """###############################

            """
        for err in errors:
            message += """
            {0}
            """.format(
                err
            )
        message += """###############################
            {0} error types in {1} records:
            ###############################""".format(
            len(errors), exceptions_count
        )
        logger.error(message)
    else:
        logger.warn("Successful upload")


class Command(BaseCommand):
    help = """
        Loads data from public download files into Django models. Add the data to "/backend/data_distro/data_to_load". \
        If you just want one file, you can pass the name of the file with -p.

        This only works in non-production environments for now, it requires pandas.
    """

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", type=str, help="file name")

    def handle(self, *args, **kwargs):
        """
        1) Find the files for upload
        2) Grab just the files we want
        3) Load data into Django models
        4) Add DUNS relationships
        """
        if kwargs["file"] is not None:
            load_file_names = [kwargs["file"]]
            if "duns" in load_file_names:
                add_duns()
                exit()
        else:
            # dependent objects are created first
            load_file_names = [
                "findingstext_formatted22.txt",
                "findings22.txt",
                "captext_formatted22.txt",
                "cfda22.txt",
                "notes22.txt",
                "revisions22.txt",
                "agency22.txt",
                "passthrough22.txt",
                "gen22.txt",
                "cpas22.txt",
            ]

        errors, exceptions_count = load_files(load_file_names)
        # doesn't seem to be multiple eins, but need to confirm
        add_duns()
        log_results(errors, exceptions_count)