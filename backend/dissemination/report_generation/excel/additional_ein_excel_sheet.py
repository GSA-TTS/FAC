from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entries(audit):
    entries = []
    if not audit or not audit.audit:
        return [[]]
    additional_eins = audit.audit.get("additional_eins", [])
    if not additional_eins:
        return [[]]

    for ein in additional_eins:
        entries.append([audit.report_id, ein])

    return entries


additional_ein_excel_sheet = ExcelSheet(
    sheet_name="additionalein",
    column_names=["report_id", "additional_ein"],
    parse_audit_to_entries=_get_entries,
)
