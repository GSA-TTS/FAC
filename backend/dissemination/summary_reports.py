from datetime import datetime
import openpyxl as pyxl
import io
import logging

from boto3 import client as boto3_client
from botocore.client import ClientError, Config

from django.conf import settings
from fs.memoryfs import MemoryFS

from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import quote_sheetname

from dissemination.models import (
    AdditionalEin,
    AdditionalUei,
    CapText,
    FederalAward,
    Finding,
    FindingText,
    General,
    Note,
    Passthrough,
    SecondaryAuditor,
)

logger = logging.getLogger(__name__)

models = [
    AdditionalEin,
    AdditionalUei,
    CapText,
    FederalAward,
    Finding,
    FindingText,
    General,
    Note,
    Passthrough,
    SecondaryAuditor,
]


columns = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "AA",
    "AB",
    "AC",
    "AD",
    "AE",
    "AF",
    "AG",
    "AH",
    "AI",
    "AJ",
    "AK",
    "AL",
    "AM",
    "AN",
    "AO",
    "AP",
    "AQ",
    "AR",
    "AS",
    "AT",
    "AU",
    "AV",
    "AW",
    "AX",
    "AY",
    "AZ",
    "BA",
    "BB",
    "BC",
    "BD",
    "BE",
    "BF",
    "BG",
    "BH",
    "BI",
    "BJ",
]


def set_column_widths(worksheet):
    dims = {}
    for row in worksheet.rows:
        for cell in row:
            if cell.value:
                dims[cell.column] = max(
                    (dims.get(cell.column, 0), len(str(cell.value)))
                )
    for col, value in dims.items():
        worksheet.column_dimensions[columns[col - 1]].width = value


def gather_report_data_dissemination(report_ids):
    """
    Given a set of report IDs, fetch the disseminated data for each and asssemble into a dictionary with the following shape:

    {
        general: {
            field_names: [],
            entries: [],
        },
        federal_award: {
            field_names: [],
            entries: [],
        },
        ...
    }
    """

    # Make report IDs unique
    report_ids = set(report_ids)

    data = {}

    for model in models:
        model_name = model.__name__.lower()

        fields = model._meta.get_fields()
        field_names = [f.name for f in fields]

        data[model_name] = {"field_names": field_names, "entries": []}

        for report_id in report_ids:
            objects = model.objects.all().filter(report_id=report_id)
            for obj in objects:
                data[model_name]["entries"].append(
                    [getattr(obj, field_name) for field_name in field_names]
                )
    return data


def gather_report_data_pre_certification(i2d_data):
    """
    Given a sac object dict, asssemble into a dictionary with the following shape:

    {
        general: {
            field_names: [],
            entries: [],
        },
        federal_award: {
            field_names: [],
            entries: [],
        },
        ...
    }
    """

    # Map IntakeToDissemination names to the dissemination table names
    i2d_to_dissemination = {
        "Generals": General,
        "SecondaryAuditors": SecondaryAuditor,
        "FederalAwards": FederalAward,
        "Findings": Finding,
        "FindingTexts": FindingText,
        "Passthroughs": Passthrough,
        "CapTexts": CapText,
        "Notes": Note,
        "AdditionalUEIs": AdditionalUei,
        "AdditionalEINs": AdditionalEin,
    }

    # Move the IntakeToDissemination data to dissemination_data, under the proper naming scheme.
    dissemination_data = {}
    for name_i2d, model in i2d_to_dissemination.items():
        dissemination_data[model.__name__.lower()] = i2d_data.get(name_i2d)

    data = {}

    # For every model (FederalAward, CapText, etc), add the skeleton object ('field_names' and empty 'entries') to 'data'.
    # Then, for every object in the dissemination_data (objects of type FederalAward, CapText, etc) create a row (array) for the summary.
    # Every row is created by looping over the field names and appending the data.
    # We also strip tzinfo from the dates, because excel doesn't like them.
    # Once a row is created, append it to the data[ModelName]['entries'] array.
    for model in models:
        model_name = model.__name__.lower()
        fields = model._meta.get_fields()
        field_names = [f.name for f in fields]
        data[model_name] = {"field_names": field_names, "entries": []}

        for obj in dissemination_data[model_name]:
            row = []
            for field_name in field_names:
                value = getattr(obj, field_name)
                # Wipe tzinfo
                if isinstance(value, datetime):
                    value = value.replace(tzinfo=None)
                row.append(value)
            data[model_name]["entries"].append(row)

    return data


def create_workbook(data):
    workbook = pyxl.Workbook()

    for sheet_name in data.keys():
        sheet = workbook.create_sheet(sheet_name)

        # create a header row with the field names
        sheet.append(data[sheet_name]["field_names"])

        # append a new row for each entry in the dataset
        for entry in data[sheet_name]["entries"]:
            sheet.append(entry)

        # add named ranges for the columns, now that the data is loaded.
        for index, field_name in enumerate(data[sheet_name]["field_names"]):
            coordinate = f"${columns[index]}$2:${columns[index]}${2 + len(data[sheet_name]['entries'])}"
            ref = f"{quote_sheetname(sheet.title)}!{coordinate}"
            named_range = DefinedName(f"{sheet_name}_{field_name}", attr_text=ref)
            workbook.defined_names.add(named_range)

        set_column_widths(sheet)

    # remove sheet that is created during workbook construction
    workbook.remove_sheet(workbook.get_sheet_by_name("Sheet"))

    return workbook


def persist_workbook(workbook):
    s3_client = boto3_client(
        service_name="s3",
        region_name=settings.AWS_S3_PRIVATE_REGION_NAME,
        aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_PRIVATE_INTERNAL_ENDPOINT,
        config=Config(signature_version="s3v4"),
    )

    with MemoryFS() as mem_fs:
        now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"bulk-{now}.xlsx"
        s3_dir = "temp"

        workbook_write_fp = mem_fs.openbin(filename, mode="w")
        workbook.save(workbook_write_fp)
        workbook_read_fp = mem_fs.openbin(filename, mode="r")
        workbook_read_fp.seek(0)
        content = workbook_read_fp.read()
        workbook_bytes = io.BytesIO(content)

        try:
            s3_client.put_object(
                Body=workbook_bytes,
                Bucket=settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
                Key=f"{s3_dir}/{filename}",
            )
        except ClientError:
            logger.warn(f"Unable to put summary report file {filename} in S3!")
            raise

    return f"temp/{filename}"


def generate_summary_report(report_ids):
    data = gather_report_data_dissemination(report_ids)
    workbook = create_workbook(data)
    filename = persist_workbook(workbook)

    return filename


def generate_presubmission_report(i2d_data):
    data = gather_report_data_pre_certification(i2d_data)
    workbook = create_workbook(data)
    filename = persist_workbook(workbook)

    return filename
