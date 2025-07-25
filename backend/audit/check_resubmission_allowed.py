from typing import Tuple
from django.utils import timezone
from audit.models import SingleAuditChecklist


def check_resubmission_allowed(sac: SingleAuditChecklist) -> Tuple[bool, str]:
    meta = sac.resubmission_meta
    gi = sac.general_information or {}

    uei = gi.get("uei")
    year = gi.get("audit_year")
    version = gi.get("version")

    # Fallback check when version, year, uei is missing or incorrect data
    if not uei or not year or version is None or sac.id is None:
        return (
            False,
            "Audit record is incomplete and cannot be evaluated for resubmission.",
        )

    # DEPRECATED audits can never be resubmitted
    if meta and meta.get("resubmission_status") == "DEPRECATED_VIA_RESUBMISSION":
        return False, "This audit has been deprecated and cannot be resubmitted."

    # ORIGINAL_SUBMISSION + version 1 can be resubmitted
    if (
        meta
        and meta.get("resubmission_status") == "ORIGINAL_SUBMISSION"
        and version == 1
    ):
        return True, "Original audit is eligible for resubmission."

    # MOST_RECENT + version > 1 can be resubmitted
    if (
        meta
        and meta.get("resubmission_status") == "MOST_RECENT"
        and version
        and version > 1
    ):
        return True, "Most recent audit is eligible for resubmission."

    # Legacy audit (meta = None, version = 0)
    if not meta and version == 0:
        siblings = SingleAuditChecklist.objects.filter(
            general_information__uei=uei,
            general_information__audit_year=year,
        ).filter(resubmission_meta__isnull=True)

        if siblings.count() == 1:
            return True, "Legacy audit is eligible for first resubmission."

        most_recent = siblings.order_by("-transition_date__0", "-id").first()
        if sac.id != most_recent.id:
            return False, (
                f"Multiple legacy audits found for this UEI and audit year. "
                f"Only the most recent (ID={most_recent.id}) may initiate resubmission."
            )

        # Check timestamp clustering
        dates = list(siblings.values_list("transition_date", flat=True))
        if dates:
            all_dates = [d[0] if isinstance(d, list) else d for d in dates]
            if max(all_dates) - min(all_dates) < timezone.timedelta(seconds=10):
                return False, (
                    "Multiple legacy audits with close timestamps were found for the same UEI and year. "
                    "This may indicate incorrect UEI use across unrelated entities. Please contact support."
                )

        return (
            True,
            "Most recent legacy audit is eligible. Others will be linked automatically.",
        )

    return False, "Audit does not meet the criteria for resubmission."
