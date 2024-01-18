import json
import re
from datetime import timedelta

from django.conf import settings

import audit.validators
from ..workbooklib.additional_ueis import get_ueis
from ..workbooklib.additional_eins import get_eins
from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..transforms.xform_remove_hyphen_and_pad_zip import xform_remove_hyphen_and_pad_zip
from ..transforms.xform_string_to_string import string_to_string
from ..exception_utils import DataMigrationError
from ..sac_general_lib.utils import (
    xform_census_date_to_datetime,
)
from ..base_field_maps import FormFieldMap, FormFieldInDissem
from ..sac_general_lib.utils import (
    create_json_from_db_object,
)

from ..change_record import InspectionRecord, CensusRecord, GsaFacRecord


PERIOD_DICT = {"A": "annual", "B": "biennial", "O": "other"}
AUDIT_TYPE_DICT = {
    "S": "single-audit",
    "P": "program-specific",
    "A": "alternative-compliance-engagement",
}


def xform_entity_type(phrase):
    """Transforms the entity type from Census format to FAC format.
    For context, see ticket #2912.
    """
    # Transformation recorded.
    mappings = {
        r"institution\s+of\s+higher\s+education": "higher-ed",
        r"non-?profit": "non-profit",
        r"local\s+government": "local",
        r"state": "state",
        r"unknown": "unknown",
        r"trib(e|al)": "tribal",
    }
    new_phrase = string_to_string(phrase)

    # Check each pattern in the mappings with case-insensitive search
    for pattern, value in mappings.items():
        if re.search(pattern, new_phrase, re.IGNORECASE):
            track_transformations(
                "ENTITY_TYPE",
                phrase,
                "entity_type",
                value,
                "xform_entity_type",
            )
            return value
    raise DataMigrationError(
        f"Could not find a match for historic entity type '{phrase}'",
        "invalid_historic_entity_type",
    )


mappings = [
    FormFieldMap(
        "auditee_fiscal_period_start", "FYENDDATE", "fy_start_date", None, str
    ),
    FormFieldMap("auditee_fiscal_period_end", "FYENDDATE", "fy_end_date", None, str),
    FormFieldMap("audit_period_covered", "PERIODCOVERED", FormFieldInDissem, None, str),
    FormFieldMap("audit_type", "AUDITTYPE", FormFieldInDissem, None, str),
    FormFieldMap("auditee_address_line_1", "STREET1", FormFieldInDissem, None, str),
    FormFieldMap("auditee_city", "CITY", FormFieldInDissem, None, str),
    FormFieldMap(
        "auditee_contact_name", "AUDITEECONTACT", FormFieldInDissem, None, str
    ),
    FormFieldMap("auditee_contact_title", "AUDITEETITLE", FormFieldInDissem, None, str),
    FormFieldMap("auditee_email", "AUDITEEEMAIL", FormFieldInDissem, None, str),
    FormFieldMap("auditee_name", "AUDITEENAME", FormFieldInDissem, None, str),
    FormFieldMap("auditee_phone", "AUDITEEPHONE", FormFieldInDissem, None, str),
    FormFieldMap("auditee_state", "STATE", FormFieldInDissem, None, str),
    FormFieldMap(
        "auditee_uei",
        "UEI",
        FormFieldInDissem,
        None,
        xform_retrieve_uei,
    ),
    FormFieldMap(
        "auditee_zip",
        "ZIPCODE",
        FormFieldInDissem,
        None,
        xform_remove_hyphen_and_pad_zip,
    ),
    FormFieldMap("auditor_address_line_1", "CPASTREET1", FormFieldInDissem, None, str),
    FormFieldMap("auditor_city", "CPACITY", FormFieldInDissem, None, str),
    FormFieldMap("auditor_contact_name", "CPACONTACT", FormFieldInDissem, None, str),
    FormFieldMap("auditor_contact_title", "CPATITLE", FormFieldInDissem, None, str),
    FormFieldMap("auditor_country", "CPACOUNTRY", FormFieldInDissem, None, str),
    FormFieldMap("auditor_ein", "AUDITOR_EIN", FormFieldInDissem, None, str),
    FormFieldMap(
        "auditor_ein_not_an_ssn_attestation", None, None, "Y", bool
    ),  # Not in DB, not disseminated, needed for validation
    FormFieldMap("auditor_email", "CPAEMAIL", FormFieldInDissem, None, str),
    FormFieldMap("auditor_firm_name", "CPAFIRMNAME", FormFieldInDissem, None, str),
    FormFieldMap("auditor_phone", "CPAPHONE", FormFieldInDissem, None, str),
    FormFieldMap("auditor_state", "CPASTATE", FormFieldInDissem, None, str),
    FormFieldMap(
        "auditor_zip",
        "CPAZIPCODE",
        FormFieldInDissem,
        None,
        xform_remove_hyphen_and_pad_zip,
    ),
    FormFieldMap("ein", "EIN", "auditee_ein", None, str),
    FormFieldMap(
        "ein_not_an_ssn_attestation", None, None, "Y", bool
    ),  # Not in DB, not disseminated, needed for validation
    FormFieldMap(
        "is_usa_based", None, None, "Y", bool
    ),  # Not in DB, not disseminated, needed for validation
    FormFieldMap(
        "met_spending_threshold", None, None, "Y", bool
    ),  # Not in DB, not disseminated, needed for validation
    FormFieldMap(
        "multiple_eins_covered", "MULTIPLEEINS", None, None, bool
    ),  # In DB, not disseminated, needed for validation
    FormFieldMap(
        "multiple_ueis_covered", "MULTIPLEUEIS", "is_additional_ueis", None, bool
    ),
    FormFieldMap(
        "user_provided_organization_type",
        "ENTITY_TYPE",
        "entity_type",
        None,
        xform_entity_type,
    ),
    FormFieldMap(
        "secondary_auditors_exist", "MULTIPLE_CPAS", None, None, bool
    ),  # In DB, not disseminated, needed for validation
]


def xform_update_multiple_eins_flag(audit_header):
    """Updates the multiple_eins_covered flag.
    This updates does not propagate to the database, it only updates the object.
    """
    if not string_to_string(audit_header.MULTIPLEEINS):
        eins = get_eins(audit_header.DBKEY, audit_header.AUDITYEAR)
        audit_header.MULTIPLEEINS = "Y" if eins else "N"


def xform_update_multiple_ueis_flag(audit_header):
    """Updates the multiple_ueis_covered flag.
    This updates does not propagate to the database, it only updates the object.
    """
    if not string_to_string(audit_header.MULTIPLEUEIS):
        ueis = get_ueis(audit_header.DBKEY, audit_header.AUDITYEAR)
        audit_header.MULTIPLEUEIS = "Y" if ueis else "N"


def _period_covered(s):
    """Helper to transform the period covered from Census format to FAC format."""
    if s not in PERIOD_DICT:
        raise DataMigrationError(
            f"Key '{s}' not found in period coverage mapping",
            "invalid_period_coverage_key",
        )
    return PERIOD_DICT[s]


def _census_audit_type(s):
    """Helper to transform the audit type from Census format to FAC format."""

    if s not in AUDIT_TYPE_DICT:
        raise DataMigrationError(
            f"Key '{s}' not found in census audit type mapping",
            "invalid_census_audit_type_key",
        )
    return AUDIT_TYPE_DICT[s]


def xform_country(general_information, audit_header):
    """Transforms the country from Census format to FAC format."""
    # Transformation to be documented.
    auditor_country = general_information.get("auditor_country").upper()
    if auditor_country in ["US", "USA"]:
        general_information["auditor_country"] = "USA"
    elif auditor_country == "":
        valid_file = open(f"{settings.SCHEMA_BASE_DIR}/States.json")
        valid_json = json.load(valid_file)
        auditor_state = string_to_string(audit_header.CPASTATE).upper()
        if auditor_state in valid_json["UnitedStatesStateAbbr"]:
            general_information["auditor_country"] = "USA"
        else:
            raise DataMigrationError(
                f"Unable to determine auditor country. Invalid state: {auditor_state}",
                "invalid_state",
            )
    else:
        raise DataMigrationError(
            f"Unable to determine auditor country. Unknown code: {auditor_country}",
            "invalid_country",
        )

    return general_information


def xform_auditee_fiscal_period_end(general_information):
    """Transforms the fiscal period end from Census format to FAC format."""
    # Transformation to be documented.
    if general_information.get("auditee_fiscal_period_end"):
        general_information[
            "auditee_fiscal_period_end"
        ] = xform_census_date_to_datetime(
            general_information.get("auditee_fiscal_period_end")
        ).strftime(
            "%Y-%m-%d"
        )
    else:
        raise DataMigrationError(
            "Auditee fiscal period end is empty.",
            "invalid_auditee_fiscal_period_end",
        )

    return general_information


def xform_auditee_fiscal_period_start(general_information):
    """Constructs the fiscal period start from the fiscal period end"""
    # Transformation to be documented.
    fiscal_start_date = xform_census_date_to_datetime(
        general_information.get("auditee_fiscal_period_end")
    ) - timedelta(days=365)
    general_information["auditee_fiscal_period_start"] = fiscal_start_date.strftime(
        "%Y-%m-%d"
    )

    return general_information


def xform_audit_period_covered(general_information):
    """Transforms the period covered from Census format to FAC format."""
    # Transformation recorded.
    if general_information.get("audit_period_covered"):
        value_in_db = general_information["audit_period_covered"]
        general_information["audit_period_covered"] = _period_covered(
            value_in_db.upper()
        )
        track_transformations(
            "PERIODCOVERED",
            value_in_db,
            "audit_period_covered",
            general_information["audit_period_covered"],
            "xform_audit_period_covered",
        )
    else:
        raise DataMigrationError(
            f"Audit period covered is empty: {general_information.get('audit_period_covered')}",
            "invalid_audit_period_covered",
        )
    return general_information


def xform_audit_type(general_information):
    """Transforms the audit type from Census format to FAC format."""
    # Transformation recorded.
    if general_information.get("audit_type"):
        value_in_db = general_information["audit_type"]
        general_information["audit_type"] = _census_audit_type(value_in_db.upper())
        track_transformations(
            "AUDITTYPE",
            value_in_db,
            "audit_type",
            general_information["audit_type"],
            "xform_audit_type",
        )
    else:
        raise DataMigrationError(
            f"Audit type is empty: {general_information.get('audit_type')}",
            "invalid_audit_type",
        )
    return general_information


def xform_replace_empty_auditor_email(general_information):
    """Replaces empty auditor email with GSA Migration keyword"""
    # Transformation recorded.
    if not general_information.get("auditor_email"):
        general_information["auditor_email"] = settings.GSA_MIGRATION
        track_transformations(
            "CPAEMAIL",
            "",
            "auditor_email",
            general_information["auditor_email"],
            "xform_replace_empty_auditor_email",
        )
    return general_information


def track_transformations(
    census_column, census_value, gsa_field, gsa_value, transformation_functions
):
    """Tracks all transformations related to the general information data."""
    census_data = [CensusRecord(column=census_column, value=census_value).to_dict()]
    gsa_fac_data = GsaFacRecord(field=gsa_field, value=gsa_value).to_dict()
    function_names = transformation_functions.split(",")
    InspectionRecord.append_general_changes(
        {
            "census_data": census_data,
            "gsa_fac_data": gsa_fac_data,
            "transformation_functions": function_names,
        }
    )


def general_information(audit_header):
    """Generates general information JSON."""
    xform_update_multiple_eins_flag(audit_header)
    xform_update_multiple_ueis_flag(audit_header)
    general_information = create_json_from_db_object(audit_header, mappings)
    transformations = [
        xform_auditee_fiscal_period_start,
        xform_auditee_fiscal_period_end,
        xform_country,
        xform_audit_period_covered,
        xform_audit_type,
        xform_replace_empty_auditor_email,
    ]

    for transform in transformations:
        if transform == xform_country:
            general_information = transform(general_information, audit_header)
        else:
            general_information = transform(general_information)

    audit.validators.validate_general_information_complete_json(general_information)

    return general_information
