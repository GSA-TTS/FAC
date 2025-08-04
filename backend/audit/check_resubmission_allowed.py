from typing import Tuple
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
from audit.models import SingleAuditChecklist
from audit.models.constants import STATUS, RESUBMISSION_STATUS


def get_last_transition_date(sac):
    """
    Given a SingleAuditChecklist, return a datetime object of the most recent transition date.
    If no transition dates exists, return the zero date.
    """
    if sac.transition_date:
        return max(sac.transition_date)
    return datetime.min.replace(tzinfo=dt_timezone.utc)


def check_resubmission_allowed(
    sac: SingleAuditChecklist,
) -> Tuple[bool, str]:
    """
    Given a SingleAuditChecklist, determine if resubmitting the record should be allowed.
    Return a Tuple(boolean, string), where the boolean determines if resubmission is allowed
    and the string is a justification.

    A record cannot be resubmitted:
    1. If it is not already public. As in, it is not already disseminated.
    2. If essential data is missing.
    3. If it has already been deprecated by another resubmission.
    4. If we can reasonably assume that a sibling record is a more recent resubmission.
    """
    # JSON from SAC
    meta = sac.resubmission_meta or {}
    gi = sac.general_information or {}

    # String variables pulled from SAC info
    end_date = gi.get("auditee_fiscal_period_end", "")
    resub_status = meta.get("resubmission_status")
    submission_status = sac.submission_status
    auditee_uei = gi.get("auditee_uei")
    version = meta.get("version") if meta else sac.version

    # Further derived from string variables
    audit_year = int(end_date.split("-")[0])

    # SAC Status must be DISSEMINATED
    if submission_status != STATUS.DISSEMINATED:
        return (
            False,
            f"Resubmission is only allowed when the current submission is in '{STATUS.DISSEMINATED}' status. Current status: '{submission_status}'",
        )

    # Fallback check when version, year, uei is missing or incorrect data
    if not all([auditee_uei, end_date, audit_year, sac.id]) or version is None:
        return (
            False,
            "Audit record is incomplete and cannot be evaluated for resubmission.",
        )

    # ORIGINAL_SUBMISSION + version 1 can be resubmitted or MOST_RECENT + version > 1 can be resubmitted
    if resub_status in [RESUBMISSION_STATUS.ORIGINAL, RESUBMISSION_STATUS.MOST_RECENT]:
        if (resub_status == RESUBMISSION_STATUS.ORIGINAL and version == 1) or (
            resub_status == RESUBMISSION_STATUS.MOST_RECENT and version > 1
        ):
            return True, "Audit is eligible for resubmission."

    # Legacy audit (meta = None) At this point, we assume data has been curated: valid submission_status, uei, year.
    if sac.resubmission_meta is None:
        siblings = SingleAuditChecklist.objects.filter(
            general_information__auditee_uei=auditee_uei,
            general_information__auditee_fiscal_period_end__startswith=str(audit_year),
            resubmission_meta__isnull=True,
        )

        if siblings.count() == 1:
            return True, "Legacy audit is eligible for first resubmission."

        sorted_siblings = sorted(
            siblings,
            key=lambda s: (get_last_transition_date(s), s.id),
        )
        most_recent = sorted_siblings[-1]

        if sac.id != most_recent.id:
            return False, (
                f"Multiple legacy audits found for this UEI and audit year. "
                f"Only the most recent (ID={most_recent.id}) may initiate resubmission."
            )

        # Check timestamp clustering
        dates = [get_last_transition_date(s) for s in siblings]
        if len(dates) > 1 and max(dates) - min(dates) < timezone.timedelta(seconds=10):
            return False, (
                "Multiple legacy audits with close timestamps were found for the same UEI and year. "
                "This may indicate incorrect UEI use across unrelated entities. Please contact support."
            )

        return (
            True,
            "Most recent legacy audit is eligible. Others will be linked automatically.",
        )

    message = (
        "This audit has been deprecated and cannot be resubmitted."
        if resub_status == RESUBMISSION_STATUS.DEPRECATED
        else "Audit does not meet the criteria for resubmission."
    )
    return False, message
