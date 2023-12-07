import audit.validators
from datetime import date
from ..base_field_maps import FormFieldMap, FormFieldInDissem
from ..sac_general_lib.utils import (
    create_json_from_db_object,
)

# The following fields represent checkboxes on the auditor certification form.
# Since all checkboxes must be checked (meaning all fields are set to True),
# the default value for these fields is set to True. These fields are not disseminated.
# They are set to ensure that the record passes validation when saved
auditor_certification_mappings = [
    FormFieldMap("is_OMB_limited", None, FormFieldInDissem, True, bool),
    FormFieldMap("is_auditee_responsible", None, FormFieldInDissem, True, bool),
    FormFieldMap("has_used_auditors_report", None, FormFieldInDissem, True, bool),
    FormFieldMap("has_no_auditee_procedures", None, FormFieldInDissem, True, bool),
    FormFieldMap("is_FAC_releasable", None, FormFieldInDissem, True, bool),
]

# auditor_certification_date_signed is not disseminated; it is set to ensure that the record passes validation when saved.
auditor_signature_mappings = [
    FormFieldMap("auditor_name", "CPACONTACT", FormFieldInDissem, None, str),
    FormFieldMap("auditor_title", "CPATITLE", FormFieldInDissem, None, str),
    FormFieldMap(
        "auditor_certification_date_signed", None, FormFieldInDissem, None, str
    ),
]


def _xform_set_certification_date(auditor_certification):
    """Sets the default auditor certification date to current date."""
    auditor_certification["auditor_signature"][
        "auditor_certification_date_signed"
    ] = date.today().isoformat()
    return auditor_certification


def auditor_certification(audit_header):
    """Generates auditor certification JSON."""
    certification = {}
    certification["auditor_certification"] = create_json_from_db_object(
        audit_header, auditor_certification_mappings
    )
    certification["auditor_signature"] = create_json_from_db_object(
        audit_header, auditor_signature_mappings
    )
    certification = _xform_set_certification_date(certification)

    audit.validators.validate_auditor_certification_json(certification)

    return certification
