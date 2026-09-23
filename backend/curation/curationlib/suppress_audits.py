import datetime
import logging

from django.db import transaction

from audit.models import SingleAuditChecklist, SubmissionEvent, User
from audit.models.constants import RESUBMISSION_STATUS, STATUS

logger = logging.getLogger(__name__)


def _get_previous_sac(sac):
    """Return the SAC immediately preceding this SAC in its resubmission chain."""
    meta = sac.resubmission_meta or {}

    previous_row_id = meta.get("previous_row_id")
    previous_report_id = meta.get("previous_report_id")

    if previous_row_id:
        try:
            return SingleAuditChecklist.objects.get(id=previous_row_id)
        except SingleAuditChecklist.DoesNotExist as exc:
            raise ValueError(
                f"Broken resubmission chain for {sac.report_id}: "
                f"previous SAC with row id {previous_row_id} does not exist."
            ) from exc

    if previous_report_id:
        try:
            return SingleAuditChecklist.objects.get(report_id=previous_report_id)
        except SingleAuditChecklist.DoesNotExist as exc:
            raise ValueError(
                f"Broken resubmission chain for {sac.report_id}: "
                f"previous SAC {previous_report_id} does not exist."
            ) from exc

    return None


def _get_next_sac(sac):
    """Return the SAC immediately following this SAC in its resubmission chain."""
    meta = sac.resubmission_meta or {}

    next_row_id = meta.get("next_row_id")
    next_report_id = meta.get("next_report_id")

    if next_row_id:
        try:
            return SingleAuditChecklist.objects.get(id=next_row_id)
        except SingleAuditChecklist.DoesNotExist as exc:
            raise ValueError(
                f"Broken resubmission chain for {sac.report_id}: "
                f"next SAC with row id {next_row_id} does not exist."
            ) from exc

    if next_report_id:
        try:
            return SingleAuditChecklist.objects.get(report_id=next_report_id)
        except SingleAuditChecklist.DoesNotExist as exc:
            raise ValueError(
                f"Broken resubmission chain for {sac.report_id}: "
                f"next SAC {next_report_id} does not exist."
            ) from exc

    return None


def _administrative_save(sac, user):
    """Save an administratively modified disseminated/resubmitted SAC."""
    sac.save(
        administrative_override=True,
        event_user=user,
        event_type=(SubmissionEvent.EventType.FAC_ADMINISTRATIVE_RESUBMISSION_LINKAGE),
    )


def _renumber_following_sacs(sac, user):
    affected = []
    current = sac

    while current:
        meta = dict(current.resubmission_meta or {})

        previous = _get_previous_sac(current)

        if previous:
            previous_version = (previous.resubmission_meta or {}).get("version", 0)

            meta["version"] = previous_version + 1
        else:
            meta["version"] = 1

        current.resubmission_meta = meta
        _administrative_save(current, user)

        affected.append(current)
        current = _get_next_sac(current)

    return affected


def repair_resubmission_chain(sac, user):
    """
    Remove `sac` from its resubmission chain and reconnect the remaining SACs.

    Handles:
        A -> B -> C   suppress A   => B -> C
        A -> B -> C   suppress B   => A -> C
        A -> B -> C   suppress C   => A -> B
    """
    meta = sac.resubmission_meta or {}

    # No resubmission relationship to repair.
    if not meta or meta.get("version", 0) == 0:
        return []

    previous = _get_previous_sac(sac)
    next_sac = _get_next_sac(sac)

    affected = []

    # Connect previous directly to next.
    if previous:
        previous_meta = dict(previous.resubmission_meta or {})

        if next_sac:
            previous_meta["next_row_id"] = next_sac.id
            previous_meta["next_report_id"] = next_sac.report_id
            previous_meta["resubmission_status"] = RESUBMISSION_STATUS.DEPRECATED
            previous.submission_status = STATUS.RESUBMITTED

        else:
            # We're suppressing the final report in the chain.
            previous_meta.pop("next_row_id", None)
            previous_meta.pop("next_report_id", None)
            previous_meta["resubmission_status"] = RESUBMISSION_STATUS.MOST_RECENT
            previous.submission_status = STATUS.DISSEMINATED

        previous.resubmission_meta = previous_meta
        _administrative_save(previous, user)
        affected.append(previous)

    # Connect next directly to previous.
    if next_sac:
        next_meta = dict(next_sac.resubmission_meta or {})

        if previous:
            next_meta["previous_row_id"] = previous.id
            next_meta["previous_report_id"] = previous.report_id
        else:
            # We're suppressing the first report in the chain.
            next_meta.pop("previous_row_id", None)
            next_meta.pop("previous_report_id", None)

        next_sac.resubmission_meta = next_meta

        renumbered = _renumber_following_sacs(next_sac, user)

        for renumbered_sac in renumbered:
            if renumbered_sac not in affected:
                affected.append(renumbered_sac)

    return affected


@transaction.atomic
def suppress_audit(report_id, email):
    """
    Administratively suppress a disseminated audit.

    - Removes dissemination rows for the target report.
    - Repairs any resubmission chain containing the report.
    - Redisseminates affected remaining reports.
    - Marks the target SAC as FLAGGED_FOR_REMOVAL.
    """

    try:
        user = User.objects.get(email=email, is_staff=True)
    except User.DoesNotExist as exc:
        raise ValueError(f"No FAC staff user found for email: {email}") from exc

    try:
        sac = SingleAuditChecklist.objects.select_for_update().get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist as exc:
        raise ValueError(f"No SAC found for report_id: {report_id}") from exc

    if sac.submission_status not in [
        STATUS.DISSEMINATED,
        STATUS.RESUBMITTED,
    ]:
        raise ValueError(
            f"{report_id} cannot be suppressed from status " f"{sac.submission_status}."
        )

    logger.info(
        "Suppressing report %s at request of %s",
        report_id,
        email,
    )

    affected = repair_resubmission_chain(sac, user)

    # Remove the target from public dissemination.
    sac.remove_dissemination()

    # The remaining chain has changed, so regenerate its public
    # resubmission information.
    for affected_sac in affected:
        affected_sac.refresh_from_db()

        result = affected_sac.redisseminate()

        if result is not True:
            raise RuntimeError(
                "Failed to redisseminate affected report "
                f"{affected_sac.report_id}: {result}"
            )

    # This is an administrative post-dissemination transition.
    _flag_sac_for_administrative_removal(sac, user)

    logger.info(
        "Successfully suppressed report %s at request of %s",
        report_id,
        email,
    )

    return sac


def _flag_sac_for_administrative_removal(sac, user):
    """Flag a disseminated/resubmitted SAC for administrative removal."""
    sac.submission_status = STATUS.FLAGGED_FOR_REMOVAL
    sac.transition_name.append(STATUS.FLAGGED_FOR_REMOVAL)
    sac.transition_date.append(datetime.datetime.now(datetime.timezone.utc))

    sac.save(
        administrative_override=True,
        event_user=user,
        event_type=SubmissionEvent.EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
    )
