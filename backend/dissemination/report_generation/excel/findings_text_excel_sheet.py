from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entries(audit):
    if not audit or not audit.audit:
        return [[]]
    findings_text = audit.audit.get("findings_text", [])
    if not findings_text:
        return [[]]

    entries = []
    for finding in findings_text:
        entries.append(
            [
                "",  # TODO: Follow-up with what we should display here.
                audit.report_id,
                finding.get("reference_number"),  # finding_ref_number
                finding.get("contains_chart_or_table"),
                finding.get("finding_text"),  # finding_text
            ]
        )
    return entries


findings_text_excel_sheet = ExcelSheet(
    sheet_name="findingtext",
    column_names=[
        "id",
        "report_id",
        "finding_ref_number",
        "contains_chart_or_table",
        "finding_text",
    ],
    parse_audit_to_entries=_get_entries,
)
