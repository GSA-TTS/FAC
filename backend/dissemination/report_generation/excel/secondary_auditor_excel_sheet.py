from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entries(audit):
    if not audit or not audit.audit:
        return [[]]
    secondary_auditors = audit.audit.get("secondary_auditors", [])
    if not secondary_auditors:
        return [[]]

    entries = []
    for sa in secondary_auditors:
        entries.append(
            [
                audit.report_id,
                sa.get("secondary_auditor_name"),
                sa.get("secondary_auditor_ein"),
                sa.get("secondary_auditor_address_street"),
                sa.get("secondary_auditor_address_city"),
                sa.get("secondary_auditor_address_state"),
                sa.get("secondary_auditor_address_zipcode"),
                sa.get("secondary_auditor_contact_name"),
                sa.get("secondary_auditor_contact_title"),
                sa.get("secondary_auditor_contact_email"),
                sa.get("secondary_auditor_contact_phone"),
            ]
        )


secondary_auditor_excel_sheet = ExcelSheet(
    sheet_name="secondaryauditor",
    column_names=[
        "report_id",
        "auditor_name",
        "auditor_ein",
        "address_street",
        "address_city",
        "address_state",
        "address_zipcode",
        "contact_name",
        "contact_title",
        "contact_email",
        "contact_phone",
    ],
    parse_audit_to_entries=_get_entries,
)
