from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entries(audit):
    if not audit or not audit.audit:
        return [[]]
    captexts = audit.audit.get("corrective_action_plan", [])
    if not captexts:
        return [[]]

    entries = []
    for text in captexts:
        entries.append(
            [
                audit.report_id,
                text.get("reference_number"),  # finding_ref_number
                text.get("planned_action"),
                text.get("contains_chart_or_table"),
            ]
        )

    return entries


captext_excel_sheet = ExcelSheet(
    sheet_name="captext",
    column_names=[
        "report_id",
        "finding_ref_number",
        "planned_action",
        "contains_chart_or_table",
    ],
    parse_audit_to_entries=_get_entries,
)
