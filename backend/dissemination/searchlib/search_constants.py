from enum import Enum

DAS_LIMIT = 1000


class SearchFields(Enum):
    audit_years = "audit_years"
    auditee_state = "auditee_state"
    names = "names"
    uei_ein = "uei_or_eins"
    start_date = "start_date"
    end_date = "end_date"
    fy_end_month = "fy_end_month"
    entity_type = "entity_type"
    report_id = "report_id"
    alns = "alns"
    cog_oversight = "cog_or_oversight"
    federal_program_name = "federal_program_name"
    findings = "findings"
    direct_funding = "direct_funding"
    major_program = "major_program"
    passthrough_name = "passthrough_name"
    type_requirement = "type_requirement"


class OrderBy:
    fac_accepted_date = "fac_accepted_date"
    auditee_name = "auditee_name"
    auditee_uei = "auditee_uei"
    audit_year = "audit_year"
    cog_over = "cog_over"
    findings_my_aln = "findings_my_aln"
    findings_all_aln = "findings_all_aln"


class Direction:
    ascending = "ascending"
    descending = "descending"


#  Standard text fields - UEI, ALN.
text_input_delimiters = [
    ",",
    ":",
    ";",
    "-",
    " ",
]

# Report ID field. Cannot include '-'.
report_id_delimiters = [
    ",",
    ":",
    ";",
    " ",
]
