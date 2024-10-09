from django.conf import settings

from census_historical_migration.invalid_record import InvalidRecord
from .errors import (
    err_findings_count_inconsistent,
)
from collections import defaultdict


def check_findings_count_consistency(sac_dict, *_args, **_kwargs):
    """
    Checks that the number of findings mentioned in Federal Awards matches
    the number of findings referenced in Federal Awards Audit Findings.
    """

    all_sections = sac_dict.get("sf_sac_sections", {})
    federal_awards_section = all_sections.get("federal_awards") or {}
    federal_awards = federal_awards_section.get("federal_awards", [])
    findings_uniform_guidance_section = (
        all_sections.get("findings_uniform_guidance") or {}
    )
    findings_uniform_guidance = findings_uniform_guidance_section.get(
        "findings_uniform_guidance_entries", []
    )
    data_source = sac_dict.get("sf_sac_meta", {}).get("data_source", "")
    expected_award_refs_count = {}
    found_award_refs_count = defaultdict(int)
    errors = []
    if _should_skip_validation(data_source):
        return errors

    expected_award_refs_count, declared_award_ref_max_length = _get_federal_award_refs(
        federal_awards
    )
    found_award_refs_count, reported_award_ref_max_length = _get_findings_award_refs(
        findings_uniform_guidance, expected_award_refs_count
    )

    updated_expected_refs_count, updated_found_refs_count = (
        _normalize_award_ref_lengths(
            declared_award_ref_max_length,
            reported_award_ref_max_length,
            federal_awards,
            findings_uniform_guidance,
        )
    )

    if updated_expected_refs_count:
        expected_award_refs_count = updated_expected_refs_count

    if updated_found_refs_count:
        found_award_refs_count = updated_found_refs_count

    errors = _validate_findings(expected_award_refs_count, found_award_refs_count)

    return errors


def _should_skip_validation(data_source):
    # Skip this validation if it is an historical audit report with incorrect findings count
    return (
        data_source == settings.CENSUS_DATA_SOURCE
        and "check_findings_count_consistency"
        in InvalidRecord.fields["validations_to_skip"]
    )


def _get_federal_award_refs(federal_awards):
    declared_award_ref_max_length = 0
    expected_award_refs_count = {}

    for award in federal_awards:
        award_reference = award.get("award_reference")
        if award_reference:
            declared_award_ref_max_length = max(
                declared_award_ref_max_length, len(award_reference)
            )
            expected_award_refs_count[award_reference] = award["program"][
                "number_of_audit_findings"
            ]

    return expected_award_refs_count, declared_award_ref_max_length


def _get_findings_award_refs(findings_uniform_guidance, expected_award_refs_count):
    reported_award_ref_max_length = 0
    found_award_refs_count = defaultdict(int)

    for finding in findings_uniform_guidance:
        award_ref = finding["program"]["award_reference"]
        if award_ref:
            reported_award_ref_max_length = max(
                reported_award_ref_max_length, len(award_ref)
            )
            if award_ref in expected_award_refs_count:
                found_award_refs_count[award_ref] += 1

    return found_award_refs_count, reported_award_ref_max_length


def _validate_findings(expected_award_refs_count, found_award_refs_count):
    errors = []
    for award_ref, expected in expected_award_refs_count.items():
        counted = found_award_refs_count[award_ref]
        if counted != expected:
            errors.append(
                {"error": err_findings_count_inconsistent(expected, counted, award_ref)}
            )
    return errors


def _normalize_award_ref_lengths(
    declared_award_ref_max_length,
    reported_award_ref_max_length,
    federal_awards,
    findings_uniform_guidance,
):
    """
    Normalize the lengths of the award references in the Federal Awards and
    Federal Awards Audit Findings workbooks before validation.
    """
    expected_award_refs_count = {}
    found_award_refs_count = defaultdict(int)

    if declared_award_ref_max_length != reported_award_ref_max_length:
        # Determine the required padding based on the difference in lengths.
        diff = abs(reported_award_ref_max_length - declared_award_ref_max_length)
        padding = "0" * diff

        if declared_award_ref_max_length < reported_award_ref_max_length:
            # This is means the version of the Federal Awards Audit Findings workbook
            # is newer than the version of the Federal Awards workbook.
            for award in federal_awards:
                award_reference = award.get("award_reference")
                if award_reference:
                    award_reference = _pad_award_ref(award_reference, padding)
                    expected_award_refs_count[award_reference] = award["program"][
                        "number_of_audit_findings"
                    ]
            for finding in findings_uniform_guidance:
                award_ref = finding["program"]["award_reference"]
                if award_ref in expected_award_refs_count:
                    found_award_refs_count[award_ref] += 1
        else:
            # This is unlikely to happen. It means the version of
            # the Federal Awards workbook is newer than
            # the version of the Federal Awards Audit Findings workbook.
            for finding in findings_uniform_guidance:
                award_ref = finding["program"]["award_reference"]
                if award_ref:
                    award_ref = _pad_award_ref(award_ref, padding)
                    if award_ref in expected_award_refs_count:
                        found_award_refs_count[award_ref] += 1
    else:
        # No normalization needed if the lengths match
        pass

    return expected_award_refs_count, found_award_refs_count


def _pad_award_ref(award_ref, padding):
    return f"{award_ref.split('-')[0]}-{padding}{award_ref.split('-')[1]}"
