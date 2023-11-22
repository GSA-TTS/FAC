import audit.validators
from datetime import date
from census_historical_migration.workbooklib.census_models.census import (
    CensusGen22 as Gen,
)
from census_historical_migration.base_field_maps import FormFieldMap, FormFieldInDissem
from census_historical_migration.sac_general_lib.utils import (
    _create_json_from_db_object,
)

# The following fields represent checkboxes on the auditee certification form.
# Since all checkboxes must be checked (meaning all fields are set to True),
# the default value for these fields is set to True. These fields are not disseminated.
# They are set to ensure that the record passes validation when saved.
auditee_certification_mappings = [
    FormFieldMap("has_no_PII", None, FormFieldInDissem, True, bool),
    FormFieldMap("has_no_BII", None, FormFieldInDissem, True, bool),
    FormFieldMap("meets_2CFR_specifications", None, FormFieldInDissem, True, bool),
    FormFieldMap("is_2CFR_compliant", None, FormFieldInDissem, True, bool),
    FormFieldMap("is_complete_and_accurate", None, FormFieldInDissem, True, bool),
    FormFieldMap("has_engaged_auditor", None, FormFieldInDissem, True, bool),
    FormFieldMap("is_issued_and_signed", None, FormFieldInDissem, True, bool),
    FormFieldMap("is_FAC_releasable", None, FormFieldInDissem, True, bool),
]

# auditee_certification_date_signed is not disseminated; it is set to ensure that the record passes validation when saved.
auditee_signature_mappings = [
    FormFieldMap("auditee_name", "auditeename", FormFieldInDissem, None, str),
    FormFieldMap("auditee_title", "auditeetitle", FormFieldInDissem, None, str),
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


def _auditee_certification(dbkey):
    """Generates auditee certification JSON."""
    gobj: Gen = Gen.select().where(Gen.dbkey == dbkey).first()
    certification = {}
    certification["auditee_certification"] = _create_json_from_db_object(
        gobj, auditee_certification_mappings
    )
    certification["auditee_signature"] = _create_json_from_db_object(
        gobj, auditee_signature_mappings
    )
    certification = _xform_set_certification_date(certification)

    audit.validators.validate_auditee_certification_json(certification)

    return certification
