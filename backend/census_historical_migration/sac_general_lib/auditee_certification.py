# import audit.validators
from census_historical_migration.workbooklib.census_models.census import (
    CensusGen22 as Gen,
)
from census_historical_migration.base_field_maps import FormFieldMap, FormFieldInDissem
from census_historical_migration.sac_general_lib.utils import (
    _create_json_from_db_object,
)

# FIXME: Do we need this ?
# auditee_certification_mappings = [
#     FormFieldMap("has_no_PII", None, FormFieldInDissem, False, bool),
#     FormFieldMap("has_no_BII", None, FormFieldInDissem, False, bool),
#     FormFieldMap("meets_2CFR_specifications", None, FormFieldInDissem, False, bool),
#     FormFieldMap("is_2CFR_compliant", None, FormFieldInDissem, False, bool),
#     FormFieldMap("is_complete_and_accurate", None, FormFieldInDissem, False, bool),
#     FormFieldMap("has_engaged_auditor", None, FormFieldInDissem, False, bool),
#     FormFieldMap("is_issued_and_signed", None, FormFieldInDissem, False, bool),
#     FormFieldMap("is_FAC_releasable", None, FormFieldInDissem, False, bool),
# ]

auditee_signature_mappings = [
    FormFieldMap("auditee_name", "auditeename", FormFieldInDissem, None, str),
    FormFieldMap("auditee_title", "auditeetitle", FormFieldInDissem, None, str),
    # FIXME: Do we need this ?
    # FormFieldMap(
    #     "auditee_certification_date_signed", None, FormFieldInDissem, None, str
    # ),
]


def _auditee_certification(dbkey):
    gobj: Gen = Gen.select().where(Gen.dbkey == dbkey).first()
    certification = {}
    # certification["auditee_certification"] = _create_json_from_db_object(
    #     gobj, auditee_certification_mappings
    # )
    certification["auditee_signature"] = _create_json_from_db_object(
        gobj, auditee_signature_mappings
    )
    # FIXME: Do we need this ?
    # verify that the created object validates against the schema
    # audit.validators.validate_auditee_certification_json(certification)

    return certification
