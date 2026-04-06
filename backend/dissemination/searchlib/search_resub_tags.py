from audit.models.constants import RESUBMISSION_STATUS, RESUBMISSION_TAGS


def _safe_int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def add_resub_tag_data(rows):
    """
    Adds resubmission data to given rows
    Only tag if it's deprecated OR if it's the most recent amongst resubmissions
    """
    for row in rows:
        v = _safe_int(getattr(row, "resubmission_version", 0))
        resub_status = getattr(row, "resubmission_status", RESUBMISSION_STATUS.UNKNOWN)
        tag = None
        color = None

        if resub_status == RESUBMISSION_STATUS.DEPRECATED:
            tag = f"V{v} ({RESUBMISSION_TAGS.DEPRECATED})"
            color = "bg-red"
        elif v > 1 and resub_status == RESUBMISSION_STATUS.MOST_RECENT:
            tag = f"V{v} ({RESUBMISSION_TAGS.MOST_RECENT})"
            color = "bg-green"

        setattr(row, "resubmission_tag", tag)
        setattr(row, "tag_color", color)
