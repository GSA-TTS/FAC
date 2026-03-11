from typing import Iterable, Mapping, Optional
from collections.abc import MutableMapping

from audit.models.constants import RESUBMISSION_STATUS, RESUBMISSION_TAGS
from dissemination.models import General


def _safe_int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def build_resub_tag_map(rows: Iterable[General]) -> Mapping[str, Optional[str]]:
    """
    Returns a dict of report_id -> tag
    Only tag if it's deprecated OR if it's the most recent amongst resubmissions
    """
    tag_map: dict[str, Optional[str]] = {}

    for row in rows:
        v = _safe_int(getattr(row, "resubmission_version", 0))
        resub_status = getattr(row, "resubmission_status", RESUBMISSION_STATUS.UNKNOWN)
        tag = None

        if v >= 1:
            if resub_status == RESUBMISSION_STATUS.DEPRECATED:
                tag = RESUBMISSION_TAGS.DEPRECATED
            if v > 1 and resub_status == RESUBMISSION_STATUS.MOST_RECENT:
                tag = RESUBMISSION_TAGS.MOST_RECENT

        tag_map[row.report_id] = tag

    return tag_map


def attach_resubmission_tags(
    rows: Iterable[General], tag_map: Mapping[str, Optional[str]]
) -> None:

    for row in rows:
        tag = tag_map.get(row.report_id)
        color = "bg-green" if tag == RESUBMISSION_TAGS.MOST_RECENT else "bg-red"

        if isinstance(row, MutableMapping):
            row["resubmission_tag"] = tag
            row["tag_color"] = color
        else:
            setattr(row, "resubmission_tag", tag)
            setattr(row, "tag_color", color)
