from .errors import (
    err_number_of_findings_inconsistent,
)
from audit.fixtures.excel import (
    SECTION_NAMES,
)


def number_of_findings(sac_dict):
    """
    Checks that the number of findings mentioned in Federal Awards
    matches the number of rows in findings, findings text, and CAP text.
    """
    all_sections = sac_dict["sf_sac_sections"]
    federal_awards = all_sections["federal_awards"]
    findings_uniform_guidance = all_sections["findings_uniform_guidance"]
    findings_text = all_sections["findings_text"]
    corrective_action_plan = all_sections["corrective_action_plan"]
    errors = []
    total_findings_expected = 0
    if federal_awards:
        total_findings_expected = sum(
            award["program"]["number_of_audit_findings"]
            for award in federal_awards.get("federal_awards", [])
        )

    if findings_uniform_guidance:
        total_rows = len(
            findings_uniform_guidance.get("findings_uniform_guidance_entries", [])
        )
        if total_rows != total_findings_expected:
            errors.append(
                {
                    "error": err_number_of_findings_inconsistent(
                        total_findings_expected,
                        total_rows,
                        SECTION_NAMES.FEDERAL_AWARDS_AUDIT_FINDINGS,
                    )
                }
            )

    if findings_text:
        total_rows = len(findings_text.get("findings_text_entries", []))
        if total_rows != total_findings_expected:
            errors.append(
                {
                    "error": err_number_of_findings_inconsistent(
                        total_findings_expected,
                        total_rows,
                        SECTION_NAMES.AUDIT_FINDINGS_TEXT,
                    )
                }
            )

    if corrective_action_plan:
        total_rows = len(
            corrective_action_plan.get("corrective_action_plan_entries", [])
        )
        if total_rows != total_findings_expected:
            errors.append(
                {
                    "error": err_number_of_findings_inconsistent(
                        total_findings_expected,
                        total_rows,
                        SECTION_NAMES.CORRECTIVE_ACTION_PLAN,
                    )
                }
            )

    return errors
