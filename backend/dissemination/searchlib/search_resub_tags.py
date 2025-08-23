from typing import Dict, Iterable, Mapping, Optional
from collections.abc import MutableMapping
from dissemination.models import General
from audit.models.constants import RESUBMISSION_STATUS


def _tag_from_resubmission_fields(row: General) -> Optional[str]:
    status = row.resubmission_status

    if status == RESUBMISSION_STATUS.MOST_RECENT:
        return "Most Recent"
    elif status == RESUBMISSION_STATUS.DEPRECATED:
        return "Resubmitted"

    # Do not tag if status is missing or unknown
    return None


def build_resub_tag_map(rows: Iterable[General]) -> Dict[str, Optional[str]]:
    """
    Builds a mapping of report_id → tag using already-loaded data from general search results.
    """
    tag_map: Dict[str, Optional[str]] = {}

    for row in rows:
        tag = _tag_from_resubmission_fields(row)
        if tag is not None:
            tag_map[row.report_id] = tag

    return tag_map


def attach_resubmission_tags(
    rows: Iterable[General], tag_map: Mapping[str, Optional[str]]
) -> None:
    """
    Injects .resubmission_tag or ['resubmission_tag'] into each row based on the tag_map.
    """
    for row in rows:
        tag = tag_map.get(row.report_id)
        if isinstance(row, MutableMapping):
            row["resubmission_tag"] = tag
        else:
            setattr(row, "resubmission_tag", tag)
