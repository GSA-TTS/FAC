from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entries(audit):
    if not audit or not audit.audit:
        return [[]]
    notes = audit.audit.get("notes_to_sefa", {})
    if not notes:
        return [[]]
    note_entries = notes.get("notes_to_sefa_entries", [])
    if not note_entries:
        return [[]]

    entries = []
    for note_entry in note_entries:
        entries.append(
            [
                note_entry.get("seq_number"),  # id
                audit.report_id,
                note_entry.get("note_title"),
                notes.get("accounting_policies"),
                notes.get("rate_explained"),
                notes.get("is_minimis_rate_used"),
                note_entry.get("note_content"),  # content
                note_entry.get("contains_chart_or_table"),
            ]
        )


notes_to_sefa_excel_sheet = ExcelSheet(
    sheet_name="note",
    column_names=[
        "id",
        "report_id",
        "note_title",
        "accounting_policies",
        "rate_explained",
        "is_minimis_rate_used",
        "content",
        "contains_chart_or_table",
    ],
    parse_audit_to_entries=_get_entries,
)
