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
from jsonschema import validate
from jsonschema.exceptions import ValidationError
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
        str,
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
        str,
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


def is_uei_valid(uei):
    try:
        with open(f"{settings.OUTPUT_BASE_DIR}/UeiSchema.json") as schema:
            schema_json = json.load(schema)
            uei_schema = schema_json.get("properties")["uei"]
            validate(instance=uei, schema=uei_schema)
            return True
    except FileNotFoundError:
        raise DataMigrationError(
            f"UeiSchema.json file not found in {settings.OUTPUT_BASE_DIR}",
            "missing_uei_schema_json",
        )
    except json.decoder.JSONDecodeError:
        raise DataMigrationError(
            "UeiSchema.json file contains invalid JSON.", "invalid_uei_schema_json"
        )

    except ValidationError:
        return False

    except Exception as e:
        raise DataMigrationError(
            f"Error validating Auditee UEI: {e}", "cannot_valid_auditee_uei"
        )


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


def xform_update_entity_type(audit_header):
    """Updates ENTITY_TYPE.
    This updates does not propagate to the database, it only updates the object.
    """
    if string_to_string(audit_header.ENTITY_TYPE) == "":
        audit_header.ENTITY_TYPE = (
            "tribal"
            if string_to_string(audit_header.SUPPRESSION_CODE).upper() == "IT"
            else "unknown"
        )
        track_transformations(
            "ENTITY_TYPE",
            "",
            "entity_type",
            audit_header.ENTITY_TYPE,
            "xform_update_entity_type",
        )


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
    """Transforms the country from Census format to FAC format. This method is now deprecated."""
    # Transformation to be documented.
    auditor_country = string_to_string(
        general_information.get("auditor_country")
    ).upper()
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


def xform_country_v2(general_information, audit_header):
    """Transforms the country from Census format to FAC format."""
    auditor_country = string_to_string(
        general_information.get("auditor_country")
    ).upper()
    if auditor_country in ["US", "USA"]:
        general_information["auditor_country"] = "USA"
    elif auditor_country == "NON-US":
        general_information["auditor_country"] = "non-USA"
        general_information["auditor_international_address"] = audit_header.CPAFOREIGN
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
        general_information["auditee_fiscal_period_end"] = (
            xform_census_date_to_datetime(
                general_information.get("auditee_fiscal_period_end")
            ).strftime("%Y-%m-%d")
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
        audit_type = _census_audit_type(value_in_db.upper())
        if audit_type == AUDIT_TYPE_DICT["A"]:
            raise DataMigrationError(
                "Skipping ACE audit",
                "skip_ace_audit",
            )
        general_information["audit_type"] = audit_type
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


def xform_replace_empty_auditee_email(general_information):
    """Replaces empty auditee email with GSA Migration keyword"""
    # Transformation recorded.
    if not general_information.get("auditee_email"):
        general_information["auditee_email"] = settings.GSA_MIGRATION
        track_transformations(
            "AUDITEEEMAIL",
            "",
            "auditee_email",
            general_information["auditee_email"],
            "xform_replace_empty_auditee_email",
        )
    return general_information


def xform_replace_empty_auditee_contact_name(general_information):
    """Replaces empty auditee contact name with GSA Migration keyword"""
    # Transformation recorded.
    if not general_information.get("auditee_contact_name"):
        general_information["auditee_contact_name"] = settings.GSA_MIGRATION
        track_transformations(
            "AUDITEECONTACT",
            "",
            "auditee_contact_name",
            general_information["auditee_contact_name"],
            "xform_replace_empty_auditee_contact_name",
        )
    return general_information


def xform_replace_empty_or_invalid_auditee_uei_with_gsa_migration(audit_header):
    """Replaces empty or invalid auditee UEI with GSA Migration keyword"""
    # Transformation recorded.
    if not (audit_header.UEI and is_uei_valid(audit_header.UEI)):
        track_transformations(
            "UEI",
            audit_header.UEI,
            "auditee_uei",
            settings.GSA_MIGRATION,
            "xform_replace_empty_or_invalid_auditee_uei_with_gsa_migration",
        )
        audit_header.UEI = settings.GSA_MIGRATION

    return audit_header


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


def xform_replace_empty_or_invalid_auditor_ein_with_gsa_migration(general_information):
    """Replaces empty or invalid auditor EIN with GSA Migration keyword"""
    # Transformation recorded.
    if not (
        general_information.get("auditor_ein")
        and re.match(
            settings.EMPLOYER_IDENTIFICATION_NUMBER,
            general_information.get("auditor_ein"),
        )
    ):
        track_transformations(
            "AUDITOR_EIN",
            general_information.get("auditor_ein"),
            "auditor_ein",
            settings.GSA_MIGRATION,
            "xform_replace_empty_or_invalid_auditor_ein_with_gsa_migration",
        )
        general_information["auditor_ein"] = settings.GSA_MIGRATION

    return general_information


def xform_replace_empty_or_invalid_auditee_ein_with_gsa_migration(general_information):
    """Replaces empty or invalid auditee EIN with GSA Migration keyword"""
    # Transformation recorded.
    if not (
        general_information.get("ein")
        and re.match(
            settings.EMPLOYER_IDENTIFICATION_NUMBER, general_information.get("ein")
        )
    ):
        track_transformations(
            "EIN",
            general_information.get("ein"),
            "auditee_ein",
            settings.GSA_MIGRATION,
            "xform_replace_empty_or_invalid_auditee_ein_with_gsa_migration",
        )
        general_information["ein"] = settings.GSA_MIGRATION

    return general_information


def xform_audit_period_other_months(general_information, audit_header):
    """
    This method addresses cases where the reporting period spans a non-standard duration, ensuring that
    the total number of months covered is accurately accounted for. This is applicable in scenarios
    where the covered period could span any number of months, rather than fixed annual or biennial periods.
    """
    if string_to_string(audit_header.PERIODCOVERED) == "O":
        general_information["audit_period_other_months"] = str(
            audit_header.NUMBERMONTHS
        ).zfill(2)


def xform_replace_empty_zips(general_information):
    """Replaces empty auditor and auditee zipcodes with GSA Migration keyword"""
    auditor_zip = general_information.get("auditor_zip")
    is_usa_auditor = general_information.get("auditor_country") != "non-USA"

    if is_usa_auditor:
        if not auditor_zip:
            new_auditor_zip = settings.GSA_MIGRATION
        else:
            new_auditor_zip = xform_remove_hyphen_and_pad_zip(auditor_zip)

        if new_auditor_zip != auditor_zip:
            track_transformations(
                "CPAZIPCODE",
                auditor_zip,
                "auditor_zip",
                new_auditor_zip,
                "xform_replace_empty_zips",
            )
            general_information["auditor_zip"] = new_auditor_zip

    auditee_zip = general_information.get("auditee_zip")
    if not auditee_zip:
        new_auditee_zip = settings.GSA_MIGRATION
    else:
        new_auditee_zip = xform_remove_hyphen_and_pad_zip(auditee_zip)

    if new_auditee_zip != auditee_zip:
        track_transformations(
            "ZIPCODE",
            auditee_zip,
            "auditee_zip",
            new_auditee_zip,
            "xform_replace_empty_zips",
        )
        general_information["auditee_zip"] = new_auditee_zip

    return general_information


def general_information(audit_header):
    """Generates general information JSON."""
    xform_update_multiple_eins_flag(audit_header)
    xform_update_multiple_ueis_flag(audit_header)
    xform_update_entity_type(audit_header)
    xform_replace_empty_or_invalid_auditee_uei_with_gsa_migration(audit_header)
    general_information = create_json_from_db_object(audit_header, mappings)
    xform_audit_period_other_months(general_information, audit_header)
    transformations = [
        xform_auditee_fiscal_period_start,
        xform_auditee_fiscal_period_end,
        xform_country_v2,
        xform_audit_period_covered,
        xform_audit_type,
        xform_replace_empty_auditor_email,
        xform_replace_empty_auditee_email,
        xform_replace_empty_or_invalid_auditor_ein_with_gsa_migration,
        xform_replace_empty_or_invalid_auditee_ein_with_gsa_migration,
        xform_replace_empty_zips,
        xform_replace_empty_auditee_contact_name,
    ]

    for transform in transformations:
        if transform == xform_country_v2:
            general_information = transform(general_information, audit_header)
        else:
            general_information = transform(general_information)

    audit.validators.validate_general_information_complete_json(general_information)

    return general_information
