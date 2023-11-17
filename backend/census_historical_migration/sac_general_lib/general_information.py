import audit.validators
from datetime import date, timedelta
from census_historical_migration.workbooklib.census_models.census import (
    CensusGen22 as Gen,
)
from census_historical_migration.sac_general_lib.utils import (
    _census_date_to_datetime,
)
from census_historical_migration.base_field_maps import FormFieldMap, FormFieldInDissem
from census_historical_migration.sac_general_lib.utils import (
    _create_json_from_db_object,
    _boolean_field,
)

mappings = [
    FormFieldMap(
        "auditee_fiscal_period_start", "fyenddate", "fy_start_date", None, str
    ),
    FormFieldMap("auditee_fiscal_period_end", "fyenddate", "fy_end_date", None, date),
    FormFieldMap("audit_period_covered", "periodcovered", FormFieldInDissem, None, str),
    FormFieldMap("audit_type", "audittype", FormFieldInDissem, None, str),
    FormFieldMap("auditee_address_line_1", "street1", FormFieldInDissem, None, str),
    FormFieldMap("auditee_city", "city", FormFieldInDissem, None, str),
    FormFieldMap(
        "auditee_contact_name", "auditeecontact", FormFieldInDissem, None, str
    ),
    FormFieldMap("auditee_contact_title", "auditeetitle", FormFieldInDissem, None, str),
    FormFieldMap("auditee_email", "auditeeemail", FormFieldInDissem, None, str),
    FormFieldMap("auditee_name", "auditeename", FormFieldInDissem, None, str),
    FormFieldMap("auditee_phone", "auditeephone", FormFieldInDissem, None, str),
    FormFieldMap("auditee_state", "state", FormFieldInDissem, None, str),
    FormFieldMap("auditee_uei", "uei", FormFieldInDissem, None, str),
    FormFieldMap("auditee_zip", "zipcode", FormFieldInDissem, None, str),
    FormFieldMap("auditor_address_line_1", "cpastreet1", FormFieldInDissem, None, str),
    FormFieldMap("auditor_city", "cpacity", FormFieldInDissem, None, str),
    FormFieldMap("auditor_contact_name", "cpacontact", FormFieldInDissem, None, str),
    FormFieldMap("auditor_contact_title", "cpatitle", FormFieldInDissem, None, str),
    FormFieldMap("auditor_country", "cpacountry", FormFieldInDissem, None, str),
    FormFieldMap("auditor_ein", "auditor_ein", FormFieldInDissem, None, str),
    FormFieldMap("auditor_ein_not_an_ssn_attestation", None, None, True, bool),
    FormFieldMap(
        "auditor_email", "cpaemail", FormFieldInDissem, "noemailfound@noemail.com", str
    ),  # FIXME: Do we want to keep `noemailfound@noemail.com`?
    FormFieldMap("auditor_firm_name", "cpafirmname", FormFieldInDissem, None, str),
    FormFieldMap("auditor_phone", "cpaphone", FormFieldInDissem, None, str),
    FormFieldMap("auditor_state", "cpastate", FormFieldInDissem, None, str),
    FormFieldMap("auditor_zip", "cpazipcode", FormFieldInDissem, None, str),
    FormFieldMap("ein", "ein", "auditee_ein", None, str),
    FormFieldMap("ein_not_an_ssn_attestation", None, None, None, str),
    FormFieldMap("is_usa_based", None, None, True, bool),
    FormFieldMap("met_spending_threshold", None, None, True, bool),
    FormFieldMap("multiple_eins_covered", "multipleeins", None, None, bool),
    FormFieldMap(
        "multiple_ueis_covered", "multipleueis", "is_additional_ueis", None, bool
    ),
    FormFieldMap(
        "user_provided_organization_type", None, "entity_type", "unknown", str
    ),  # FIXME: There is no in_db mapping ?
    FormFieldMap("secondary_auditors_exist", "multiple_cpas", None, None, bool),
]


def _period_covered(s):
    return {"A": "annual", "B": "biennial", "O": "other"}[s]


def _census_audit_type(s):
    return {
        "S": "single-audit",
        "P": "program-specific",
        "A": "alternative-compliance-engagement",
    }[s]


def _xform_country(gen):
    gen["auditor_country"] = "USA" if gen.get("auditor_country") == "US" else "non-USA"
    return gen


def _xform_email(gen):
    gen["auditor_email"] = gen.get("auditor_email", "noemailfound@noemail.com")
    return gen


def _xform_auditee_fiscal_period_end(gen):
    gen["auditee_fiscal_period_end"] = _census_date_to_datetime(
        gen.get("auditee_fiscal_period_end")
    ).strftime("%Y-%m-%d")
    return gen


def _xform_auditee_fiscal_period_start(gen):
    fiscal_start_date = _census_date_to_datetime(
        gen.get("auditee_fiscal_period_end")
    ) - timedelta(days=365)
    gen["auditee_fiscal_period_start"] = fiscal_start_date.strftime("%Y-%m-%d")
    return gen


def _xform_audit_period_covered(gen):
    gen["audit_period_covered"] = _period_covered(gen.get("audit_period_covered"))
    return gen


def _xform_audit_type(gen):
    gen["audit_type"] = _census_audit_type(gen.get("audit_type"))
    return gen


def _xform_multiple_eins_covered(gen):
    return _boolean_field(gen, "multiple_eins_covered")


def _xform_multiple_ueis_covered(gen):
    return _boolean_field(gen, "multiple_ueis_covered")


def _xform_secondary_auditors_exist(gen):
    return _boolean_field(gen, "secondary_auditors_exist")


def _general_information(dbkey):
    gobj: Gen = Gen.select().where(Gen.dbkey == dbkey).first()

    general_information = _create_json_from_db_object(gobj, mappings)

    # List of transformation functions
    transformations = [
        _xform_auditee_fiscal_period_start,
        _xform_auditee_fiscal_period_end,
        _xform_country,
        _xform_email,
        _xform_audit_period_covered,
        _xform_audit_type,
        _xform_multiple_eins_covered,
        _xform_multiple_ueis_covered,
        _xform_secondary_auditors_exist,
    ]

    # Apply transformations
    for transform in transformations:
        general_information = transform(general_information)

    # verify that the created object validates against the schema
    audit.validators.validate_general_information_complete_json(general_information)

    return general_information
