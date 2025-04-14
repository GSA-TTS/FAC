"""
Each validator added must be imported and added to the functions list below.

Each validator should be a single function in a single file.
The name of the function should match the name of the file.

Each validator function should take a dictionary as its only argument; this
dictionary has these top-level fields:

    sf_sac_sections
    sf_sac_meta

sf_sac_sections has these fields:

    general_information
    federal_awards
    corrective_action_plan
    findings_text
    findings_uniform_guidance
    additional_ueis

Each of those contains a list or dict representing that section.
These are already Python objects; no JSON deserialization is required.

sf_sac_meta contains all of the fields that are not in the sections; currently
these are:

    submitted_by
    date_created
    submission_status
    report_id
    audit_type
    transition_name
    transition_date

The function cross_validation.sac_validation_shape will take a
SingleAuditChecklist instance and convert it into a dictionary with the above
structure.

Each validator function should return either an empty list if there are no
errors or a list of dicts where each dict has a single field, "error", that
has a string describing the error as its value.
This value is intended to be shown to the user.

So, the no-errors return value is:

    []

And an example with-errors return value is:

    [
        {
            "error": "Your attempt at humor has been denied by the committee."
        }
    ]

"""

from .additional_ueis import additional_ueis
from .auditee_ueis_match import auditee_ueis_match
from .check_award_ref_declaration import check_award_ref_declaration
from .check_award_ref_existence import check_award_ref_existence
from .check_award_reference_uniqueness import check_award_reference_uniqueness
from .check_finding_prior_references import check_finding_prior_references
from .check_biennial_low_risk import check_biennial_low_risk
from .check_certifying_contacts import check_certifying_contacts
from .check_finding_reference_uniqueness import check_finding_reference_uniqueness
from .check_findings_count_consistency import check_findings_count_consistency
from .check_has_federal_awards import check_has_federal_awards
from .check_ref_number_in_cap import check_ref_number_in_cap
from .check_ref_number_in_findings_text import check_ref_number_in_findings_text
from .submission_progress_check import submission_progress_check
from .tribal_data_sharing_consent import tribal_data_sharing_consent
from .validate_general_information import validate_general_information

functions = [
    additional_ueis,
    auditee_ueis_match,
    check_award_ref_existence,
    check_award_ref_declaration,
    check_award_reference_uniqueness,
    check_biennial_low_risk,
    check_certifying_contacts,
    check_finding_reference_uniqueness,
    check_finding_prior_references,
    check_findings_count_consistency,
    check_has_federal_awards,
    check_ref_number_in_cap,
    check_ref_number_in_findings_text,
    submission_progress_check,
    tribal_data_sharing_consent,
    validate_general_information,
]
