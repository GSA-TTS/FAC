DAS_LIMIT = 1000


class ORDER_BY:
    fac_accepted_date = "fac_accepted_date"
    auditee_name = "auditee_name"
    auditee_uei = "auditee_uei"
    audit_year = "audit_year"
    cog_over = "cog_over"
    findings_my_aln = "findings_my_aln"
    findings_all_aln = "findings_all_aln"


class DIRECTION:
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
