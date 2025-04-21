import string
import uuid
import time
import openpyxl as pyxl

from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import quote_sheetname

from dissemination.report_generation.excel.coversheets import (
    note_coversheet_excel_sheet,
)
from dissemination.report_generation.excel.findings_excel_sheet import (
    findings_excel_sheet,
)
from dissemination.report_generation.excel.additional_ein_excel_sheet import (
    additional_ein_excel_sheet,
)
from dissemination.report_generation.excel.additional_uei_excel_sheet import (
    additional_uei_excel_sheet,
)
from dissemination.report_generation.excel.cap_text_excel_sheet import (
    captext_excel_sheet,
)
from dissemination.report_generation.excel.federal_awards_excel_sheet import (
    federal_awards_excel,
)
from dissemination.report_generation.excel.findings_text_excel_sheet import (
    findings_text_excel_sheet,
)
from dissemination.report_generation.excel.general_excel_sheet import (
    general_information_excel,
)
from dissemination.report_generation.excel.notes_excel_sheet import (
    notes_to_sefa_excel_sheet,
)
from dissemination.report_generation.excel.passthrough_excel_sheet import (
    passthrough_excel_sheet,
)
from dissemination.report_generation.excel.secondary_auditor_excel_sheet import (
    secondary_auditor_excel_sheet,
)

REPORT_FORMAT = [
    additional_ein_excel_sheet,
    additional_uei_excel_sheet,
    captext_excel_sheet,
    federal_awards_excel,
    findings_excel_sheet,
    findings_text_excel_sheet,
    federal_awards_excel,
    general_information_excel,
    notes_to_sefa_excel_sheet,
    note_coversheet_excel_sheet,
    passthrough_excel_sheet,
    secondary_auditor_excel_sheet,
]

columns = list(string.ascii_uppercase)
columns += ["A" + ch for ch in string.ascii_uppercase]
columns += ["B" + ch for ch in "ABCDEFGHIJ"]


def create_workbook(data, protect_sheets=False):
    t0 = time.time()
    workbook = pyxl.Workbook()
    # remove sheet that is created during workbook construction
    default_sheet = workbook.active
    workbook.remove(default_sheet)
    for sheet_name in sorted(data.keys()):
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
        if protect_sheets:
            protect_sheet(sheet)

    t1 = time.time()
    return workbook, t1 - t0


def set_column_widths(worksheet):
    dims = {}
    for row in worksheet.rows:
        for cell in row:
            if cell.value:
                dims[cell.column] = max(
                    (dims.get(cell.column, 0), len(str(cell.value)))
                )
    for col, value in dims.items():
        # Pad the column by a bit, so things are not cramped.
        worksheet.column_dimensions[columns[col - 1]].width = int(value * 1.2)


def protect_sheet(sheet):
    sheet.protection.sheet = True
    sheet.protection.password = str(uuid.uuid4())
    sheet.protection.enable()
