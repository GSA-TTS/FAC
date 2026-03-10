from typing import Iterable, Mapping, Optional
from collections.abc import MutableMapping

from audit.models.constants import RESUBMISSION_STATUS
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
        v = _safe_int(getattr(row, "resubmission_version", None))
        resub_status = getattr(row, "resubmission_status", RESUBMISSION_STATUS.UNKNOWN)

        if v < 1 or (v == 1 and resub_status == RESUBMISSION_STATUS.MOST_RECENT):
            tag_map[row.report_id] = None
        elif v >= 1:
            if resub_status == RESUBMISSION_STATUS.DEPRECATED:
                tag_map[row.report_id] = "Resubmitted"
            if resub_status == RESUBMISSION_STATUS.MOST_RECENT:
                tag_map[row.report_id] = "Most Recent"

    return tag_map


def attach_resubmission_tags(
    rows: Iterable[General], tag_map: Mapping[str, Optional[str]]
) -> None:

    for row in rows:
        tag = tag_map.get(row.report_id)
        if isinstance(row, MutableMapping):
            row["resubmission_tag"] = tag
        else:
            setattr(row, "resubmission_tag", tag)
