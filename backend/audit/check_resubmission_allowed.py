from typing import Tuple
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
from audit.models import SingleAuditChecklist
from audit.models.constants import STATUS, RESUBMISSION_STATUS


def get_last_transition_date(sac):
    if sac.transition_date:
        return max(sac.transition_date)
    return datetime.min.replace(tzinfo=dt_timezone.utc)


def check_resubmission_allowed(
    sac: SingleAuditChecklist,
) -> Tuple[bool, str]:  # noqa: C901
    meta = sac.resubmission_meta or {}
    gi = sac.general_information or {}

    uei = gi.get("auditee_uei")
    end_date = gi.get("auditee_fiscal_period_end")
    version = meta.get("version") if meta else sac.version
    submission_status = sac.submission_status
    resub_status = meta.get("resubmission_status")

    # SAC Status must be DISSEMINATED
    if submission_status != STATUS.DISSEMINATED:
        return (
            False,
            f"Resubmission is only allowed when the current submission is in '{STATUS.DISSEMINATED}' status. Current status: '{submission_status}'",
        )

    # Audit Year
    try:
        audit_year = int(end_date.split("-")[0])
    except Exception:
        audit_year = None

    # Fallback check when version, year, uei is missing or incorrect data
    if not all([uei, end_date, audit_year, sac.id]) or version is None:
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
            general_information__auditee_uei=uei,
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
