def audit_findings(sac_dict):
    """
    Checks that the number of audit findings in the Federal Awards and Audit Findings
    sections are consistent.
    """
    all_sections = sac_dict["sf_sac_sections"]
    awards_outer = all_sections.get("federal_awards", {})
    awards = awards_outer.get("federal_awards", []) if awards_outer else []
    finds_outer = all_sections.get("findings_text", {})
    findings = finds_outer.get("findings_text_entries", []) if finds_outer else []
    # If both empty, that's consistent:
    if not awards and not findings:
        return []
    if awards:
        # How to determine if findings is required? Loop through the awards?
        num_expected = sum(_.get("number_of_audit_findings", 0) for _ in findings)
        # For now, just check for non-zero
        if num_expected and not awards:
            return [
                {
                    "error": "There are findings listed in Federal Awards "
                    " but none in Findings Text"
                }
            ]

    if False > 1:
        return [{"error": "error message"}]
    return []
