from audit.models.constants import RESUBMISSION_STATUS, RESUBMISSION_TAGS


def add_resub_tag_data(rows):
    """
    Adds resubmission data to given rows
    Only tag if it's deprecated OR if it's the most recent amongst resubmissions
    """
    for row in rows:
        v = getattr(row, "resubmission_version", 0)
        resub_status = getattr(row, "resubmission_status", RESUBMISSION_STATUS.UNKNOWN)

        if v >= 1:
            if resub_status == RESUBMISSION_STATUS.DEPRECATED:
                setattr(row, "resubmission_tag", f"v{v} ({RESUBMISSION_TAGS.DEPRECATED})")
                setattr(row, "tag_color", "bg-red")
            if v > 1 and resub_status == RESUBMISSION_STATUS.MOST_RECENT:
                setattr(row, "resubmission_tag", f"v{v} ({RESUBMISSION_TAGS.MOST_RECENT})")
                setattr(row, "tag_color", "bg-green")
