import audit.validators
from datetime import date
from ..base_field_maps import FormFieldMap, FormFieldInDissem
from ..sac_general_lib.utils import (
    create_json_from_db_object,
)

# The following fields represent checkboxes on the auditee certification form.
# Since all checkboxes must be checked (meaning all fields are set to True),
# the default value for these fields is set to `Y`. These fields are not disseminated.
# They are set to ensure that the record passes validation when saved.
auditee_certification_mappings = [
    FormFieldMap("has_no_PII", None, FormFieldInDissem, "Y", bool),
    FormFieldMap("has_no_BII", None, FormFieldInDissem, "Y", bool),
    FormFieldMap("meets_2CFR_specifications", None, FormFieldInDissem, "Y", bool),
    FormFieldMap("is_2CFR_compliant", None, FormFieldInDissem, "Y", bool),
    FormFieldMap("is_complete_and_accurate", None, FormFieldInDissem, "Y", bool),
    FormFieldMap("has_engaged_auditor", None, FormFieldInDissem, "Y", bool),
    FormFieldMap("is_issued_and_signed", None, FormFieldInDissem, "Y", bool),
    FormFieldMap("is_FAC_releasable", None, FormFieldInDissem, "Y", bool),
]

# auditee_certification_date_signed is not disseminated; it is set to ensure that the record passes validation when saved.
auditee_signature_mappings = [
    FormFieldMap("auditee_name", "AUDITEENAME", FormFieldInDissem, None, str),
    FormFieldMap("auditee_title", "AUDITEETITLE", FormFieldInDissem, None, str),
    FormFieldMap(
        "auditee_certification_date_signed", None, FormFieldInDissem, None, str
    ),
]


def _xform_set_certification_date(auditee_certification):
    """Sets the default auditee certification date to today's date."""
    auditee_certification["auditee_signature"][
        "auditee_certification_date_signed"
    ] = date.today().isoformat()
    return auditee_certification


def auditee_certification(audit_header):
    """Generates auditee certification JSON."""
    certification = {}
    certification["auditee_certification"] = create_json_from_db_object(
        audit_header, auditee_certification_mappings
    )
    certification["auditee_signature"] = create_json_from_db_object(
        audit_header, auditee_signature_mappings
    )
    certification = _xform_set_certification_date(certification)

    audit.validators.validate_auditee_certification_json(certification)

    return certification
