from datetime import datetime, timezone
from dissemination.report_generation.excel.excel_sheet import ExcelSheet
from django.conf import settings


limit_disclaimer = f"This spreadsheet contains the first {settings.SUMMARY_REPORT_DOWNLOAD_LIMIT} results of your search. If you need to download more than {settings.SUMMARY_REPORT_DOWNLOAD_LIMIT} submissions, try limiting your search parameters to download in batches."
can_read_tribal_disclaimer = "This document includes one or more Tribal entities that have chosen to keep their data private per 2 CFR 200.512(b)(2). Because your account has access to these submissions, this document includes their audit findings text, corrective action plan, and notes to SEFA. Don't share this data outside your agency."
cannot_read_tribal_disclaimer = "This document includes one or more Tribal entities that have chosen to keep their data private per 2 CFR 200.512(b)(2). It doesn't include their audit findings text, corrective action plan, or notes to SEFA."


def insert_precert_coversheet(workbook):
    # Importing here to avoid circular dependencies.
    from dissemination.report_generation.excel.utils import (
        set_column_widths,
        protect_sheet,
    )

    sheet = workbook.create_sheet("Coversheet", 0)
    sheet.append(
        ["Time created", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")]
    )
    sheet.append(["Note", "This file is for review only and can't be edited."])
    set_column_widths(sheet)
    protect_sheet(sheet)


def insert_dissemination_coversheet(workbook, contains_tribal, include_private):
    # Importing here to avoid circular dependencies.
    from dissemination.report_generation.excel.utils import set_column_widths

    sheet = workbook.create_sheet("Coversheet", 0)
    sheet.append(
        ["Time created", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")]
    )
    sheet.append(
        [
            "Note",
            limit_disclaimer,
        ]
    )

    if contains_tribal:
        if include_private:
            sheet.append(
                [
                    "Note",
                    can_read_tribal_disclaimer,
                ]
            )
        else:
            sheet.append(
                [
                    "Note",
                    cannot_read_tribal_disclaimer,
                ]
            )

    # Uncomment if we want to link to the FAC API for larger data dumps.
    # sheet.cell(row=3, column=2).value = "FAC API Link"
    # sheet.cell(row=3, column=2).hyperlink = f"{settings.STATIC_SITE_URL}/developers/"
    set_column_widths(sheet)


def _get_entries(audit):
    if not audit or not audit.audit:
        return [[]]
    notes = audit.audit.get("notes_to_sefa", {})
    if not notes:
        return [[]]

    return [
        [
            audit.report_id,
            notes["accounting_policies"],
            notes["rate_explained"],
            notes["is_minimis_rate_used"],
        ]
    ]


note_coversheet_excel_sheet = ExcelSheet(
    sheet_name="note_coversheet",
    column_names=[
        "report_id",
        "accounting_policies",
        "rate_explained",
        "is_minimis_rate_used",
    ],
    parse_audit_to_entries=_get_entries,
)
