import audit.validators
from datetime import date
from census_historical_migration.workbooklib.census_models.census import (
    CensusGen22 as Gen,
)
from census_historical_migration.base_field_maps import FormFieldMap, FormFieldInDissem
from census_historical_migration.sac_general_lib.utils import (
    _create_json_from_db_object,
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
    FormFieldMap("auditor_name", "cpacontact", FormFieldInDissem, None, str),
    FormFieldMap("auditor_title", "cpatitle", FormFieldInDissem, None, str),
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


def _auditor_certification(dbkey):
    gobj: Gen = Gen.select().where(Gen.dbkey == dbkey).first()
    certification = {}
    certification["auditor_certification"] = _create_json_from_db_object(
        gobj, auditor_certification_mappings
    )
    certification["auditor_signature"] = _create_json_from_db_object(
        gobj, auditor_signature_mappings
    )
    certification = _xform_set_certification_date(certification)

    audit.validators.validate_auditor_certification_json(certification)

    return certification
