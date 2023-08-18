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
from .check_award_ref_existence import check_award_ref_existence
from .number_of_findings import number_of_findings
from .additional_ueis import additional_ueis
from .auditee_ueis_match import auditee_ueis_match
from .award_ref_and_references_uniqueness import award_ref_and_references_uniqueness
from .sac_validation_shape import sac_validation_shape  # noqa: F401
from .submission_progress_check import submission_progress_check
from .tribal_data_sharing_consent import tribal_data_sharing_consent

functions = [
    auditee_ueis_match,
    additional_ueis,
    check_award_ref_existence,
    award_ref_and_references_uniqueness,
    number_of_findings,
    submission_progress_check,
    tribal_data_sharing_consent,
]
