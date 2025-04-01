"""
The intent of this file is to group together audit related helpers.
"""

import logging


from datetime import timedelta
from django.utils import timezone as django_timezone
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Func

from audit.models.constants import FindingsBitmask, FINDINGS_FIELD_TO_BITMASK
from support.cog_over_w_audit import compute_cog_over

logger = logging.getLogger(__name__)

import json


def generate_sac_report_id(count, end_date, source="GSAFAC"):
    """
    Convenience method for generating report_id, a value consisting of:

        -   Four-digit year based on submission fiscal end date.
        -   Two-digit month based on submission fiscal end date.
        -   Audit source: either GSAFAC or CENSUS.
        -   Zero-padded 10-digit numeric monotonically increasing.
        -   Separated by hyphens.

    For example: `2023-09-GSAFAC-0000000001`, `2020-09-CENSUS-0000000001`.
    """
    source = source.upper()
    if source not in ("CENSUS", "GSAFAC"):
        raise Exception("Unknown source for report_id")
    year, month, _ = end_date.split("-")
    if not (2000 <= int(year) < 2200):
        raise Exception("Unexpected year value for report_id")
    if int(month) not in range(1, 13):
        raise Exception("Unexpected month value for report_id")
    separator = "-"
    report_id = separator.join([year, month, source, str(count).zfill(10)])
    return report_id


class JsonArrayToTextArray(Func):
    function = "json_array_to_text_array"
    output_field = ArrayField(models.CharField())


def one_month_from_today():
    return django_timezone.now() + timedelta(days=30)


def camel_to_snake(raw: str) -> str:
    """Convert camel case to snake_case."""
    text = f"{raw[0].lower()}{raw[1:]}"
    return "".join(c if c.islower() else f"_{c.lower()}" for c in text)


def generate_audit_indexes(audit):
    general_information = audit.audit.get("general_information", {})

    fiscal_period_end = general_information.get("auditee_fiscal_period_end", None)
    if fiscal_period_end:
        audit_year, fy_end_month, _ = fiscal_period_end.split("-")
    else:
        audit_year, fy_end_month, _ = "1900-01-01".split("-")

    cognizant_agency, oversight_agency = compute_cog_over(
        audit.audit["federal_awards"],
        audit.submission_status,
        audit.auditee_ein,
        audit.auditee_uei,
        audit.audit_year,
    )

    is_public = general_information.get(
        "user_provided_organization_type", ""
    ) != "tribal" or audit.audit.get("tribal_data_consent", {}).get(
        "is_tribal_information_authorized_to_be_public", True
    )
    awards_indexes = _index_awards(audit.audit)
    findings_indexes = _index_findings(audit.audit)
    general_indexes = _index_general(audit.audit)

    return {
        "audit_year": audit_year,
        "cognizant_agency": cognizant_agency,
        "oversight_agency": oversight_agency,
        "fy_end_month": fy_end_month,
        "is_public": is_public,
        "search_indexes": {**findings_indexes, **awards_indexes, **general_indexes},
    }


def _index_findings(audit_data):
    findings = 0
    compliance_requirements = set()
    unique_findings = set()
    for finding in audit_data.get("findings_uniform_guidance", []):
        for mask in FINDINGS_FIELD_TO_BITMASK:
            if finding.get(mask.field, "N") == "Y":
                findings |= mask.mask
        if finding.get("findings", {}).get("repeat_prior_reference", "N") == "Y":
            findings |= FindingsBitmask.REPEAT_FINDING

        compliance_requirement = finding.get("program", {}).get(
            "compliance_requirement", ""
        )
        compliance_requirements.add(compliance_requirement)

        reference_number = finding.get("findings", {}).get("reference_number", None)
        if reference_number:
            unique_findings.add(reference_number)

    return {
        "findings_summary": findings,
        "compliance_requirements": list(compliance_requirements),
        "unique_audit_findings_count": len(unique_findings),
    }


def _index_awards(audit_data):
    """
    Method for pulling out all the data from awards that we search on, to improve
    search performance.
    """
    program_names = []
    passthrough_names = set()
    agency_prefixes = set()
    agency_extensions = set()
    has_direct_funding = False
    has_indirect_funding = False
    is_major_program = False

    for award in audit_data.get("federal_awards", {}).get("awards", []):
        program = award.get("program", {})
        if program.get("program_name", ""):
            program_names.append(award["program"]["program_name"])
        if program.get("is_major", "N") == "Y":
            is_major_program = True
        agency_prefixes.add(program.get("federal_agency_prefix", ""))
        agency_extensions.add(program.get("three_digit_extension", ""))

        if award.get("direct_or_indirect_award", {}).get("is_direct", "") == "Y":
            has_direct_funding = True
        elif award.get("direct_or_indirect_award", {}).get("is_direct", "") == "N":
            has_indirect_funding = True
        passthrough_names.update(
            [
                entity.get("passthrough_name", None)
                for entity in award.get("direct_or_indirect_award", {}).get(
                    "entities", []
                )
            ]
        )

    return {
        "program_names": program_names,
        "has_direct_funding": has_direct_funding,
        "has_indirect_funding": has_indirect_funding,
        "is_major_program": is_major_program,
        "passthrough_names": list(passthrough_names),
        "agency_extensions": list(agency_extensions),
        "agency_prefixes": list(agency_prefixes),
    }


def _index_general(audit_data):

    general_information = audit_data.get("general_information", {})

    search_names = set()
    general_fields = [
        "auditee_contact_name",
        "auditee_email",
        "auditee_name",
        "auditor_contact_name",
        "auditor_email",
        "auditor_firm_name",
    ]
    for field in general_fields:
        search_names.add(general_information.get(field, ""))

    # Also search over certification
    auditee_certify_name = (
        audit_data.get("auditee_certification", {})
        .get("auditee_signature", {})
        .get("auditee_name", "")
    )
    auditor_certify_name = (
        audit_data.get("auditor_certification", {})
        .get("auditor_signature", {})
        .get("auditor_name", "")
    )

    search_names.add(auditee_certify_name)
    search_names.add(auditor_certify_name)

    return {
        "search_names": list(search_names),
    }


# TESTING functions to check data in SAC and Audit
def validate_audit_consistency(audit_instance):
    """
    Validates that all data in SingleAuditChecklist exists in Audit,
    ignores strucutre and searches for keys/values. All values in SAC,
    must exist in Audit.
    """
    from audit.models import SingleAuditChecklist

    sac = SingleAuditChecklist

    try:
        sac_instance = sac.objects.get(report_id=audit_instance.report_id)
    except:
        return False, [
            {"error": f"No SAC found with report_id {audit_instance.report_id}"}
        ]

    differences = []

    json_fields_to_check = [
        "general_information",
        "federal_awards",
        "findings_text",
        "findings_uniform_guidence",
        "corrective_action_plan",
        "additional_ueis",
        "additional_eins",
        "secondary_auditors",
        "notes_to_sefa",
        "audit_information",
        "auditor_certification",
        "auditee_certification",
        "tribal_data_consent",
    ]

    simple_fields_to_check = [
        "audit_type",
        "data_source",
        "cognizant_agency",
        "oversight_agency",
    ]

    for field in simple_fields_to_check:
        sac_value = getattr(sac_instance, field, None)
        audit_value = getattr(audit_instance, field, None)

        if sac_value and sac_value != audit_value:
            differences.append(
                {"field": field, "sac_value": sac_value, "audit_value": audit_value}
            )

    for field in json_fields_to_check:
        sac_data = getattr(sac_instance, field, None)
        audit_field_data = audit_instance.audit.get(field)

        if sac_data is not None and audit_field_data in [None, {}]:
            differences.append(
                {
                    "field": field,
                    "error": f"Field is empty in Audit, but not in SAC",
                    "sac_value": sac_data,
                    "audit_value": None,
                }
            )
            continue

        if sac_data is None and audit_field_data not in [None, {}]:
            differences.append(
                {
                    "field": field,
                    "error": f"Field is empty in SAC, but not in Audit",
                    "sac_value": None,
                    "audit_value": audit_field_data,
                }
            )
            continue

        if sac_data is not None:
            flat_sac = flatten_json(sac_data)
            flat_audit = flatten_json(audit_instance.audit)

            for (
                sac_path,
                sac_value,
            ) in flat_sac.items():

                normalized_sac_path = sac_path.split(".")[-1]
                match_found = False

                for audit_path, audit_value in flat_audit.items():
                    normalized_audit_path = audit_path.split(".")[-1]

                    if (
                        normalized_sac_path == normalized_audit_path
                        and sac_value == audit_value
                    ):
                        match_found = True
                        break

                if not match_found:
                    result = value_exists_in_audit(sac_path, sac_value, flat_audit)

                    if not result.get("found"):
                        differences.append(
                            {
                                "field": field,
                                "sac_path": sac_path,
                                "sac_value": sac_value,
                                "error": f"Value from SAC.{field}.{sac_path} not found in Audit",
                            }
                        )

                    elif result.get("found_with_different_format"):
                        differences.append(
                            {
                                "field": field,
                                "sac_path": sac_path,
                                "sac_value": sac_value,
                                **result,
                            }
                        )

                    elif result.get("found_with_different_key"):
                        differences.append(
                            {
                                "field": field,
                                "sac_path": sac_path,
                                "sac_value": sac_value,
                                "audit_path": result["audit_path"],
                                "error": f"Value from SAC.{field}.{sac_path} found in Audit but with different structure/key",
                            }
                        )

    return len(differences) == 0, differences


def flatten_json(obj, path="", result=None):
    """Flatten a nested JSON into kv pair with path"""
    if result is None:
        result = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            flatten_json(value, new_path, result)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            flatten_json(item, new_path, result)
    else:
        result[path] = obj

    return result


def value_exists_in_audit(sac_path, sac_value, audit_data):
    """Check if a value from SAC exists somewhere in audit data with the same key-value"""
    sac_field = sac_path.split(".")[-1] if "." in sac_path else sac_path
    sac_field = sac_field.split("[")[0] if "[" in sac_field else sac_field

    sac_norm_field = normalize_key(sac_field)

    for audit_path, audit_value in audit_data.items():
        audit_field = audit_path.split(".")[-1] if "." in audit_path else audit_path
        audit_field = audit_field.split("[")[0] if "[" in audit_field else audit_field

        audit_norm_field = normalize_key(audit_field)

        if normalize_key(audit_field) != sac_norm_field:
            continue

        if sac_value == audit_value:
            if sac_field != audit_field:
                return {
                    "found": True,
                    "found_with_different_key": True,
                    "sac_field": sac_field,
                    "audit_path": audit_path,
                    "value": audit_value,
                }
            return {
                "found": True,
            }
        elif (
            not isinstance(sac_value, bool)
            and sac_value != 0
            and other_formats_match(sac_value, audit_value).get("found")
        ):
            comp_vals = other_formats_match(sac_value, audit_value)
            if sac_field != audit_field:
                return {
                    "found": True,
                    "found_with_different_key": True,
                    "found_with_different_format": True,
                    "sac_field": sac_field,
                    "audit_path": audit_path,
                    "value": audit_value,
                    **comp_vals,
                }
            else:
                return {"found_with_different_format": True, **comp_vals}

    if not isinstance(sac_value, bool) and sac_value != 0:
        for audit_path, audit_value in audit_data.items():
            audit_field = audit_path.split(".")[-1] if "." in audit_path else audit_path
            audit_field = (
                audit_field.split("[")[0] if "[" in audit_field else audit_field
            )

            if normalize_key(audit_field) == sac_norm_field:
                continue

            if sac_value == audit_value:
                return {
                    "found": True,
                    "found_with_different_key": True,
                    "sac_field": sac_field,
                    "audit_path": audit_path,
                    "value": audit_value,
                }
            elif other_formats_match(sac_value, audit_value).get("found"):
                comp_vals = other_formats_match(sac_value, audit_value)
                return {
                    "found": True,
                    "found_with_different_key": True,
                    "found_with_different_format": True,
                    "sac_field": sac_field,
                    "audit_path": audit_path,
                    "value": audit_value,
                    **comp_vals,
                }

    return {
        "found": False,
    }


def normalize_key(key):
    """Normalize the keys for comparison"""
    if not isinstance(key, str):
        return key

    normalized = key.replace("-", "_")
    return normalized.lower()


def other_formats_match(value1, value2):
    """Determines if value1 matches value2 but in a different format"""
    if isinstance(value1, list) and value2 in value1:
        return {"found": True, "error": f"{value1} is list, found {value2}"}

    if isinstance(value2, list) and value1 in value2:
        return {"found": True, "error": f"{value2} is list, found {value1}"}

    if isinstance(value1, dict) and value2 in value1.values():
        return {"found": True, "error": f"{value1} is dict, found {value2}"}

    if isinstance(value2, dict) and value1 in value2.values():
        return {"found": True, "error": f"{value2} is dict, found {value1}"}

    try:
        # Zeroes create false positives when comparing values like "00" or False
        if value1 == 0 or value2 == 0:
            return {"found": False}

        if isinstance(value1, (int, float)) and isinstance(value2, str):
            if value1 == float(value2):
                return {
                    "found": True,
                    "error": f"{value1} is int/float, found {value2} as string",
                }
        if isinstance(value2, (int, float)) and isinstance(value1, str):
            if value2 == float(value1):
                return {
                    "found": True,
                    "error": f"{value2} is int/float, found {value1} as string",
                }
    except (ValueError, TypeError):
        pass

    return {"found": False}
