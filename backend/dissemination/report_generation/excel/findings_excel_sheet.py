from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entries(audit):
    if not audit or not audit.audit:
        return [[]]
    findings = audit.audit.get("findings_uniform_guidance", [])
    if not findings:
        return [[]]

    awards = audit.audit.get("federal_awards", {}).get("awards", [])
    awards_dict = {award.get("award_reference"): award for award in awards}

    entries = []
    for finding in findings:
        award = awards_dict.get(finding.get("program", {}).get("award_reference"))
        award_program = award.get("program", {})
        entries.append(
            [
                audit.report_id,
                award_program.get("federal_agency_prefix"),
                award_program.get("three_digit_extension"),  # federal_award_extension
                f"{award_program.get('federal_agency_prefix')}.{award_program.get('three_digit_extension')}",  # aln,
                finding.get("program", {}).get("award_reference"),
                finding.get("findings", {}).get("reference_number"),
                finding.get("program", {}).get(
                    "compliance_requirement"
                ),  # type_requirement
                finding.get("modified_opinion"),  # is_modified_opinion
                finding.get("other_findings"),  # is_other_findings
                finding.get("material_weakness"),  # is_material_weakness
                finding.get("significant_deficiency"),  # is_significant_deficiency
                finding.get("other_matters"),  # is_other_matters
                finding.get("questioned_costs"),  # is_questioned_costs
                finding.get("findings", {}).get(
                    "repeat_prior_reference"
                ),  # is_repeat_finding",
                finding.get("findings", {}).get(
                    "prior_references"
                ),  # prior_finding_ref_numbers",
            ]
        )


findings_excel_sheet = ExcelSheet(
    sheet_name="finding",
    column_names=[
        "report_id",
        "federal_agency_prefix",
        "federal_award_extension",
        "aln",
        "award_reference",
        "reference_number",
        "type_requirement",
        "is_modified_opinion",
        "is_other_findings",
        "is_material_weakness",
        "is_significant_deficiency",
        "is_other_matters",
        "is_questioned_costs",
        "is_repeat_finding",
        "prior_finding_ref_numbers",
    ],
    parse_audit_to_entries=_get_entries,
)
