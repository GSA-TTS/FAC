from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entries(audit):
    if not audit or not audit.audit:
        return [[]]
    passthrough_items = audit.audit.get("passthrough", [])
    if not passthrough_items:
        return [[]]

    entries = []
    for passthrough in passthrough_items:
        entries.append(
            [
                audit.report_id,
                passthrough.get("award_reference"),
                passthrough.get("passthrough_name"),
                passthrough.get("passthrough_id"),
            ]
        )
    return entries


passthrough_excel_sheet = ExcelSheet(
    sheet_name="passthrough",
    column_names=[
        "report_id",
        "award_reference",
        "passthrough_name",
        "passthrough_id",
    ],
    parse_audit_to_entries=_get_entries,
)
