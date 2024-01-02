import json
import re
from datetime import timedelta

from django.conf import settings

import audit.validators
from ..api_test_helpers import extract_api_data
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

from ..change_record import ChangeRecord, CensusRecord, GsaFacRecord


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
            # FIXME-MSHD: This is a transformation that we may want to record
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
    FormFieldMap(
        "audit_type", "AUDITTYPE", FormFieldInDissem, None, str
    ),  # FIXME: It appears the audit_type attribute is duplicated in the sac object: it exists both in the object and in the general_information section.
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
    auditor_country = general_information.get("auditor_country").upper()
    census_data = [
        CensusRecord(column="CPACOUNTRY", value=general_information["auditor_country"]).to_dict()
    ]
    if auditor_country in ["US", "USA"]:
        general_information["auditor_country"] = "USA"
        gsa_fac_data = [
            GsaFacRecord(
                field="auditor_country", value=general_information["auditor_country"]
            ).to_dict()
        ]
    elif auditor_country == "":
        valid_file = open(f"{settings.SCHEMA_BASE_DIR}/States.json")
        valid_json = json.load(valid_file)
        auditor_state = string_to_string(audit_header.CPASTATE).upper()
        if auditor_state in valid_json["UnitedStatesStateAbbr"]:
            general_information["auditor_country"] = "USA"
            gsa_fac_data = [
                GsaFacRecord(
                    field="auditor_country",
                    value=general_information["auditor_country"],
                ).to_dict()
            ]
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

    return general_information, census_data, gsa_fac_data


def xform_auditee_fiscal_period_end(general_information):
    """Transforms the fiscal period end from Census format to FAC format."""
    if general_information.get("auditee_fiscal_period_end"):
        census_data = [
            CensusRecord(
                column="FYENDDATE",
                value=general_information["auditee_fiscal_period_end"],
            ).to_dict()
        ]
        general_information[
            "auditee_fiscal_period_end"
        ] = xform_census_date_to_datetime(
            general_information.get("auditee_fiscal_period_end")
        ).strftime(
            "%Y-%m-%d"
        )
        gsa_fac_data = [
            GsaFacRecord(
                field="auditee_fiscal_period_end",
                value=general_information["auditee_fiscal_period_end"],
            ).to_dict()
        ]
    else:
        raise DataMigrationError(
            f"Auditee fiscal period end is empty: {general_information.get('auditee_fiscal_period_end')}",
            "invalid_auditee_fiscal_period_end",
        )

    return general_information, census_data, gsa_fac_data


def xform_auditee_fiscal_period_start(general_information):
    """Constructs the fiscal period start from the fiscal period end"""
    census_data = [
        CensusRecord(
            column="FYENDDATE",
            value=general_information["auditee_fiscal_period_start"],
        ).to_dict()
    ]
    fiscal_start_date = xform_census_date_to_datetime(
        general_information.get("auditee_fiscal_period_end")
    ) - timedelta(days=365)
    general_information["auditee_fiscal_period_start"] = fiscal_start_date.strftime(
        "%Y-%m-%d"
    )
    gsa_fac_data = [
        GsaFacRecord(
            field="auditee_fiscal_period_start",
            value=general_information["auditee_fiscal_period_start"],
        ).to_dict()
    ]

    return general_information, census_data, gsa_fac_data


def xform_audit_period_covered(general_information):
    """Transforms the period covered from Census format to FAC format."""
    if general_information.get("audit_period_covered"):
        census_data = [
            CensusRecord(
                column="PERIODCOVERED",
                value=general_information["audit_period_covered"],
            ).to_dict()
        ]
        general_information["audit_period_covered"] = _period_covered(
            general_information.get("audit_period_covered").upper()
        )
        gsa_fac_data = [
            GsaFacRecord(
                field="audit_period_covered",
                value=general_information["audit_period_covered"],
            ).to_dict
        ]
    else:
        raise DataMigrationError(
            f"Audit period covered is empty: {general_information.get('audit_period_covered')}",
            "invalid_audit_period_covered",
        )
    return general_information, census_data, gsa_fac_data


def xform_audit_type(general_information):
    """Transforms the audit type from Census format to FAC format."""
    if general_information.get("audit_type"):
        census_data = [
            CensusRecord(column="AUDITTYPE", value=general_information["audit_type"]).to_dict()
        ]
        general_information["audit_type"] = _census_audit_type(
            general_information.get("audit_type").upper()
        )
        gsa_fac_data = [
            GsaFacRecord(field="audit_type", value=general_information["audit_type"]).to_dict()
        ]
    else:
        raise DataMigrationError(
            f"Audit type is empty: {general_information.get('audit_type')}",
            "invalid_audit_type",
        )
    return general_information, census_data, gsa_fac_data


def track_transformation(census_data, gsa_fac_data, transformations):
    ChangeRecord.extend_general_changes(
        [
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_function": transformations,
            }
        ]
    )


def general_information(audit_header):
    """Generates general information JSON."""

    general_information = create_json_from_db_object(audit_header, mappings)

    transformations = [
        xform_auditee_fiscal_period_start,
        xform_auditee_fiscal_period_end,
        xform_country,
        xform_audit_period_covered,
        xform_audit_type,
    ]

    for transform in transformations:
        if transform == xform_country:
            general_information, census_data, gsa_fac_data = transform(
                general_information, audit_header
            )
        else:
            general_information, census_data, gsa_fac_data = transform(
                general_information
            )
        track_transformation(census_data, gsa_fac_data, [transform.__name__])

    audit.validators.validate_general_information_complete_json(general_information)

    api_data = extract_api_data(mappings, general_information)

    return (general_information, api_data)
