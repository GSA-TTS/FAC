from typing import Iterable, Mapping, Optional, Tuple
from collections.abc import MutableMapping

from dissemination.models import General


def _safe_int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def build_resub_tag_map(rows: Iterable[General]) -> Mapping[str, Optional[str]]:
    """
    report_id -> tag

    Since everything is marked MOST_RECENT in the DB, we treat "is part of a resub chain"
    as: resubmission_version > 1.

    Per (auditee_uei, audit_year):
      - the row with the highest version => "Most Recent"
      - all other rows with version > 1 => "Resubmitted"
      - version <= 1 (or missing) => no tag
    """

    # (uei, year) -> best score (version, accepted_date, report_id) for stable tie-breaking
    best_score_by_group: dict[Tuple[str, str], tuple] = {}
    winner_report_id_by_group: dict[Tuple[str, str], str] = {}

    # 1) find the winner per group among rows where version > 1
    for row in rows:
        v = _safe_int(getattr(row, "resubmission_version", None))
        if v <= 1:
            continue

        key = (row.auditee_uei, row.audit_year)

        acc = getattr(row, "fac_accepted_date", None)
        # if date is None, keep it low so real dates win ties
        score = (v, acc or 0, row.report_id)

        if key not in best_score_by_group or score > best_score_by_group[key]:
            best_score_by_group[key] = score
            winner_report_id_by_group[key] = row.report_id

    # 2) assign tags
    tag_map: dict[str, Optional[str]] = {}

    for row in rows:
        v = _safe_int(getattr(row, "resubmission_version", None))
        if v <= 1:
            tag_map[row.report_id] = None
            continue

        key = (row.auditee_uei, row.audit_year)
        if winner_report_id_by_group.get(key) == row.report_id:
            tag_map[row.report_id] = "Most Recent"
        else:
            tag_map[row.report_id] = "Resubmitted"

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
