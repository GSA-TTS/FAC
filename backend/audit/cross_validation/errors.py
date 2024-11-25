from audit.fixtures.excel import (
    SECTION_NAMES,
)
from .utils import format_refs


def err_additional_ueis_empty():
    return (
        "general_information.multiple_ueis_covered is checked, "
        "but no additonal UEIs were found."
    )


def err_additional_ueis_has_auditee_uei():
    return "The additional UEIs list includes the auditee UEI."


def err_additional_ueis_not_empty():
    return (
        "general_information.multiple_ueis_covered is marked false, "
        "but additonal UEIs were found."
    )


def err_auditee_ueis_match():
    return "Not all auditee UEIs matched."


def err_awards_findings_but_no_findings_text():
    return "There are findings indicated in Federal Awards but" "none in Findings Text."


def err_missing_tribal_data_sharing_consent():
    return (
        "As a tribal organization, the Auditee Certifying Official must complete "
        "the data sharing consent statement before submitting your audit."
    )


def err_unexpected_tribal_data_sharing_consent():
    return "Tribal consent privacy flag set but non-tribal org type."


def err_certifying_contacts_should_not_match():
    return "The certifying auditor and auditee should not have the same email address."


def err_biennial_low_risk():
    return (
        "According to Uniform Guidance section 200.520(a), biennial audits cannot "
        "be considered 'low-risk.' Please make the necessary changes to the 'Audit "
        "Period Covered' or indicate that the auditee did NOT qualify as low-risk."
    )


def err_duplicate_finding_reference(award_ref, ref_number):
    return f"Award {award_ref} repeats reference {ref_number}. The reference {ref_number} should only appear once for award {award_ref}."


def err_prior_no_report(auditee_uei, prior_ref_number):
    return f"Findings uniform guidance contains prior reference {prior_ref_number}, but no previous reports were found for UEI {auditee_uei}."


def err_prior_ref_not_found(prior_ref_number):
    return f"Prior reference number {prior_ref_number} not found in previous reports."


def err_findings_count_inconsistent(total_expected, total_counted, award_ref):
    return (
        f"You reported {total_expected} findings for award {award_ref} in the {SECTION_NAMES.FEDERAL_AWARDS} workbook, "
        f"but declared {total_counted} findings for the same award in the {SECTION_NAMES.FEDERAL_AWARDS_AUDIT_FINDINGS} workbook."
    )


def err_duplicate_award_reference(award_ref):
    return (
        f"The award reference {award_ref} shows up more than once. "
        f"This should not be possible. Please contact customer support."
    )


def err_award_ref_not_declared(award_refs: list):
    is_plural = len(award_refs) > 1
    if is_plural:
        award_refs_str = (
            ", ".join(str(ar) for ar in award_refs[:-1]) + " and " + str(award_refs[-1])
        )
    else:
        award_refs_str = str(award_refs[0])

    return (
        f"Award{'s' if is_plural else ''} {award_refs_str} {'are' if is_plural else 'is'} reported in the "
        f"{SECTION_NAMES.FEDERAL_AWARDS_AUDIT_FINDINGS} workbook, but {'were' if is_plural else 'was'} not "
        f"declared in the {SECTION_NAMES.FEDERAL_AWARDS} workbook."
    )


def err_missing_award_reference(row_num):
    return (
        f"The award listed in row {row_num} of your Federal Award workbook is missing a reference code. "
        f"This should not be possible. Please contact customer support."
    )


def err_missing_or_extra_references(
    missing_refs: set, extra_refs: set, section_name: str
) -> str:
    messages = [f"In the {section_name} workbook"]

    if missing_refs:
        messages.append(f"you are missing the references: {format_refs(missing_refs)}")

    if extra_refs:
        messages.append(
            f"{'and also ' if missing_refs else ''}you have some extra references: {format_refs(extra_refs)}"
        )

    return ", ".join(messages) + "."


def err_no_federal_awards():
    return "This submission contains no federal awards."
