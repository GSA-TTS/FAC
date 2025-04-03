from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entries(audit):
    if not audit or not audit.audit:
        return [[]]
    awards = audit.audit.get("federal_awards", {}).get("awards", [])
    if not awards:
        return [[]]

    entries = []
    for award in awards:
        program = award.get("program", {})
        loan = award.get("loan_or_loan_guarantee", {})
        entries.append(
            [
                audit.report_id,
                award.get("award_reference"),
                program.get("federal_agency_prefix"),
                program.get("three_digit_extension"),  # federal_award_extension
                f"{program.get("federal_agency_prefix")}.{program.get("three_digit_extension")}",  # aln,
                award.get("program").get("number_of_audit_findings"),  # findings_count
                program.get("additional_award_identification"),
                program.get("program_name"),  # federal_program_name
                program.get("amount_expended"),
                program.get("federal_program_total"),
                award.get("cluster").get("cluster_name"),
                award.get("cluster").get("state_cluster_name"),
                award.get("cluster").get("other_cluster_name"),
                award.get("cluster").get("cluster_total"),
                award.get("direct_or_indirect_award").get("is_direct"),
                award.get("subrecipients", {}).get(
                    "is_passed", "N"
                ),  # "is_passthrough_award"
                award.get("subrecipients", {}).get(
                    "subrecipient_amount"
                ),  # "passthrough_amount"
                program.get("is_major"),
                program.get("audit_report_type"),
                loan.get("is_guaranteed", "N"),  # is_loan"
                loan.get("loan_balance_at_audit_period_end", ""),  # "loan_balance"
            ]
        )

    return entries


federal_awards_excel = ExcelSheet(
    sheet_name="federalaward",
    column_names=[
        "report_id",
        "award_reference",
        "federal_agency_prefix",
        "federal_award_extension",
        "aln",
        "findings_count",
        "additional_award_identification",
        "federal_program_name",
        "amount_expended",
        "federal_program_total",
        "cluster_name",
        "state_cluster_name",
        "other_cluster_name",
        "cluster_total",
        "is_direct",
        "is_passthrough_award",
        "passthrough_amount",
        "is_major",
        "audit_report_type",
        "is_loan",
        "loan_balance",
    ],
    parse_audit_to_entries=_get_entries,
)
