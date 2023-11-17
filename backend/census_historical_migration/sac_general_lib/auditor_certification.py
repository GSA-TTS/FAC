# import audit.validators
from census_historical_migration.workbooklib.census_models.census import (
    CensusGen22 as Gen,
)
from census_historical_migration.base_field_maps import FormFieldMap, FormFieldInDissem
from census_historical_migration.sac_general_lib.utils import (
    _create_json_from_db_object,
)

# FIXME: Do we need this ?
# auditor_certification_mappings = [
#     FormFieldMap("is_OMB_limited", None, FormFieldInDissem, False, bool),
#     FormFieldMap("is_auditee_responsible", None, FormFieldInDissem, False, bool),
#     FormFieldMap("has_used_auditors_report", None, FormFieldInDissem, False, bool),
#     FormFieldMap("has_no_auditee_procedures", None, FormFieldInDissem, False, bool),
#     FormFieldMap("is_FAC_releasable", None, FormFieldInDissem, False, bool),
# ]

auditor_signature_mappings = [
    FormFieldMap("auditor_name", "cpacontact", FormFieldInDissem, None, str),
    FormFieldMap("auditor_title", "cpatitle", FormFieldInDissem, None, str),
    # FIXME: Do we need this ?
    # FormFieldMap(
    #     "auditor_certification_date_signed", None, FormFieldInDissem, None, str
    # ),
]


def _auditor_certification(dbkey):
    gobj: Gen = Gen.select().where(Gen.dbkey == dbkey).first()
    certification = {}
    # auditor_certification["auditor_certification"] = _create_json_from_db_object(
    #     gobj, auditor_certification_mappings
    # )
    certification["auditor_signature"] = _create_json_from_db_object(
        gobj, auditor_signature_mappings
    )
    # FIXME: Do we need this ?
    # verify that the created object validates against the schema
    # audit.validators.validate_auditor_certification_json(certification)

    return certification
