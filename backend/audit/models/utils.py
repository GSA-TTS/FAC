"""
The intent of this file is to group together audit related helpers.
"""

import logging


from datetime import timedelta

import pytz
from django.utils import timezone as django_timezone
from django.contrib.postgres.fields import ArrayField
from django.db import models, connection
from django.db.models import Func

from audit.models.constants import FindingsBitmask, FINDINGS_FIELD_TO_BITMASK
from support.cog_over_w_audit import compute_cog_over

logger = logging.getLogger(__name__)


def get_next_sequence_id(sequence_name):
    """Get the next ID from the given sequence."""

    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval(%s);", [sequence_name])
        return cursor.fetchall()[0][0]


def generate_sac_report_id(sequence, end_date, source="GSAFAC"):
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
    report_id = separator.join([year, month, source, str(sequence).zfill(10)])
    return report_id


class JsonArrayToTextArray(Func):
    function = "json_array_to_text_array"
    output_field = ArrayField(models.CharField())


def one_month_from_today():
    return django_timezone.now() + timedelta(days=30)


def one_year_from_today():
    return django_timezone.now() + timedelta(days=365)


def camel_to_snake(raw: str) -> str:
    """Convert camel case to snake_case."""
    text = f"{raw[0].lower()}{raw[1:]}"
    return "".join(c if c.islower() else f"_{c.lower()}" for c in text)


def convert_utc_to_american_samoa_zone(date):
    us_samoa_zone = pytz.timezone("US/Samoa")
    # Ensure the datetime object is time zone aware
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        date = pytz.utc.localize(date)
    # Convert to American Samoa timezone (UTC-11)
    american_samoa_time = date.astimezone(us_samoa_zone)
    # Extract the date and format it as YYYY-MM-DD
    formatted_date = american_samoa_time.strftime("%Y-%m-%d")

    return formatted_date


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
        int(audit_year),
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
