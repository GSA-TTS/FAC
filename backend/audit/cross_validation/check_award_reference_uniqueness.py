from .errors import (
    err_duplicate_award_reference,
)
from collections import Counter


def check_award_reference_uniqueness(sac_dict, *_args, **_kwargs):
    """
    Check that all award references in the Federal Award workbook are distinct.
    """

    all_sections = sac_dict.get("sf_sac_sections", {})
    federal_awards_section = all_sections.get("federal_awards") or {}
    federal_awards = federal_awards_section.get("federal_awards", [])
    award_refs = []
    errors = []

    for award in federal_awards:
        award_reference = award.get("award_reference", None)
        if award_reference:
            award_refs.append(award_reference)

    duplicated_award_refs = _find_duplicates(award_refs)

    for dup_award_ref in duplicated_award_refs:
        errors.append({"error": err_duplicate_award_reference(dup_award_ref)})

    return errors


def _find_duplicates(lst):
    count = Counter(lst)
    return [item for item, count in count.items() if count > 1]
