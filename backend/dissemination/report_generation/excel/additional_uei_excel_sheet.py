from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entries(audit):
    entries = []
    if not audit or not audit.audit:
        return [[]]
    additional_ueis = audit.audit.get("additional_ueis", [])
    if not additional_ueis:
        return [[]]

    for uei in additional_ueis:
        entries.append([audit.report_id, uei])

    return entries


additional_uei_excel_sheet = ExcelSheet(
    sheet_name="additionaluei",
    column_names=["report_id", "additional_uei"],
    parse_audit_to_entries=_get_entries,
)
