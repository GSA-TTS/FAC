import json

from jsonschema import FormatChecker, validate
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError
from django.core.exceptions import ValidationError
from django.conf import settings

from audit.cross_validation.naming import NC
from audit.validators import validate_general_information_schema_rules
from .errors import err_biennial_low_risk


required_fields = {
    #  `key_in_json_schema: label_for_user`
    "audit_type": "Type of audit",
    "auditee_address_line_1": "Auditee street",
    "auditee_city": "Auditee city",
    "auditee_zip": "Auditee ZIP",
    "auditee_contact_name": "Auditee contact name",
    "auditee_contact_title": "Auditee contact title",
    "auditee_email": "Auditee email",
    "auditee_fiscal_period_end": "Fiscal period end date",
    "auditee_fiscal_period_start": "Fiscal period start date",
    "auditee_name": "Auditee name",
    "auditee_phone": "Auditee phone",
    "auditee_state": "Auditee state",
    "auditee_uei": "Auditee UEI",
    "auditor_contact_name": "Auditor contact name",
    "auditor_contact_title": "Auditor contact title",
    "auditor_ein": "Auditor EIN",
    "auditor_ein_not_an_ssn_attestation": "Confirmation that auditor EIN is not an SSN",
    "auditor_email": "Auditor email",
    "auditor_firm_name": "Audit firm name",
    "auditor_phone": "Auditor phone number",
    "ein": "Auditee EIN",
    "ein_not_an_ssn_attestation": "Confirmation that auditee EIN is not an SSN",
    "is_usa_based": "Auditor is USA-based",
    "met_spending_threshold": "Spending threshold",
    "multiple_eins_covered": "Multiple EINs covered",
    "multiple_ueis_covered": "Multiple UEIs covered",
    "secondary_auditors_exist": "Confirmation that secondary auditors exist",
    "user_provided_organization_type": "Organization type",
    "audit_period_covered": "Audit period",
}

# optionally_required_fields is handled separately from required_fields
optionally_required_fields = {
    "auditor_state": "Auditor state",
    "auditor_zip": "Auditor ZIP",
    "auditor_address_line_1": "Auditor street",
    "auditor_city": "Auditor city",
    "auditor_country": "Auditor country",
    "auditor_international_address": "Auditor international address",
}


def validate_general_information(sac_dict, *_args, **_kwargs):
    """
    Runs the general information data through JSON Schema validation.

    This largely repeats logic in
    audit.validators.validate_general_information_json,
    but that function doesn't pass along the full error context and we need that here.

    The errors this presents to the user are arcane, but should make clear that they
    must return to the General Information page, and once there they will get
    friendlier errors when they try to proceed.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "GeneralInformationRequired.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    all_sections = sac_dict["sf_sac_sections"]
    general_information = all_sections[NC.GENERAL_INFORMATION]
    errors = _check_required_field(general_information)

    audit_information = all_sections[NC.AUDIT_INFORMATION]
    errors.extend(_check_biennial_low_risk(general_information, audit_information))

    if errors:
        return errors
    try:
        validate_general_information_schema_rules(general_information)
        validate(general_information, schema, format_checker=FormatChecker())
    except JSONSchemaValidationError as err:
        return [{"error": f"General Information: {str(err)}"}]
    except ValidationError as err:
        return [{"error": f"General Information: {str(err.message)}"}]
    return []


def _check_required_field(general_information):
    """
    Check that all required fields are present in the general information.
    """
    # Check that all required fields are present or return a message pointing to the missing fields
    missing_fields = []
    for key, label in required_fields.items():
        if key not in general_information or general_information[key] in [None, ""]:
            missing_fields.append(label)

    if missing_fields:
        return [{"error": f"Missing required fields: {', '.join(missing_fields)}"}]

    return []


def _check_biennial_low_risk(general_information, audit_information):
    """
    Check that both biennial and low risk flags aren't both set.
    """
    if (
        general_information["audit_period_covered"] == "biennial"
        and audit_information["is_low_risk_auditee"]
    ):
        return [{"error": err_biennial_low_risk}]
    else:
        return []
