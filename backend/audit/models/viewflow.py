from audit.models import SingleAuditChecklist, SubmissionEvent, Audit
from audit.models.constants import EventType, STATUS
from audit.models.utils import convert_utc_to_american_samoa_zone
from curation.curationlib.curation_audit_tracking import CurationTracking
import datetime
import logging
import viewflow.fsm

logger = logging.getLogger(__name__)

# TODO: Update Post SOC Launch -> This whole file will need updating


def sac_revert_from_submitted(sac, audit=None):
    """
    Transitions the submission_state for a SingleAuditChecklist back
    to "auditee_certified" so the user can re-address issues and submit.
    This should only be executed via management command.
    """

    if sac.submission_status == STATUS.SUBMITTED:
        flow = SingleAuditChecklistFlow(sac)

        flow.transition_to_auditee_certified()

        with CurationTracking():
            sac.save(
                event_user=None,
                event_type=SubmissionEvent.EventType.AUDITEE_CERTIFICATION_COMPLETED,
            )
        return True

    if audit and audit.submission_status == STATUS.SUBMITTED:
        flow = AuditFlow(audit)

        flow.transition_to_auditee_certified()

        with CurationTracking():
            audit.save(
                event_user=None,
                event_type=SubmissionEvent.EventType.AUDITEE_CERTIFICATION_COMPLETED,
            )
        return True
    return False


def sac_revert_from_flagged_for_removal(sac, user, audit=None):
    """
    Transitions the submission_state for a SingleAuditChecklist back
    to "in_progress" so the user can continue working on it.
    This should be accessible to django admin.
    """
    if sac.submission_status == STATUS.FLAGGED_FOR_REMOVAL:
        flow = SingleAuditChecklistFlow(sac)

        flow.transition_to_in_progress_again()

        with CurationTracking():
            sac.save(
                event_user=user,
                event_type=SubmissionEvent.EventType.CANCEL_REMOVAL_FLAG,
            )

    # undo the flagged status for the audit as well.
    if audit and audit.submission_status == STATUS.FLAGGED_FOR_REMOVAL:
        audit_revert_from_flagged_for_removal(audit, user)


def audit_revert_from_flagged_for_removal(audit, user):
    """
    Transitions the submission_state for an Audit back
    to "in_progress" so the user can continue working on it.
    This should be accessible to django admin.
    """
    if audit and audit.submission_status == STATUS.FLAGGED_FOR_REMOVAL:
        flow = AuditFlow(audit)

        flow.transition_to_in_progress_again()

        with CurationTracking():
            audit.save(
                event_user=user,
                event_type=SubmissionEvent.EventType.CANCEL_REMOVAL_FLAG,
            )


def sac_flag_for_removal(sac, user, audit=None):
    """
    Transitions the submission_state for a SingleAuditChecklist to "flagged_for_removal".
    This should be accessible to django admin.
    """
    if sac.submission_status == STATUS.IN_PROGRESS:
        flow = SingleAuditChecklistFlow(sac)

        flow.transition_to_flagged_for_removal()

        with CurationTracking():
            sac.save(
                event_user=user,
                event_type=SubmissionEvent.EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
            )

    if audit and audit.submission_status == STATUS.IN_PROGRESS:
        audit_flag_for_removal(audit, user)


def audit_flag_for_removal(audit, user):
    """
    Transitions the submission_state for an Audit to "flagged_for_removal".
    This should be accessible to django admin.
    """
    if audit and audit.submission_status == STATUS.IN_PROGRESS:
        flow = AuditFlow(audit)
        flow.transition_to_flagged_for_removal()
        with CurationTracking():
            audit.save(
                event_user=user,
                event_type=SubmissionEvent.EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
            )


def sac_transition(request, sac, **kwargs):
    """
    Transitions the submission_state for a SingleAuditChecklist (sac).
    """
    audit = kwargs.get("audit", None)
    user = None
    flow = SingleAuditChecklistFlow(sac)
    audit_flow = AuditFlow(audit)

    target = kwargs.get("transition_to", None)

    # optional - only needed when a user is involved.
    if request:
        user = request.user

    # SAC must transition to a target state.
    if target is None:
        return False

    if target == STATUS.IN_PROGRESS:
        flow.transition_to_in_progress_again()
        sac.save(
            event_user=user,
            event_type=SubmissionEvent.EventType.UNLOCKED_AFTER_CERTIFICATION,
        )
        _transition_audit(
            audit=audit,
            user=user,
            submission_event=EventType.UNLOCKED_AFTER_CERTIFICATION,
            autoflow_action=audit_flow.transition_to_in_progress_again,
        )
        return True

    elif target == STATUS.FLAGGED_FOR_REMOVAL:
        flow.transition_to_flagged_for_removal()
        sac.save(
            event_user=user,
            event_type=SubmissionEvent.EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
        )
        _transition_audit(
            audit=audit,
            user=user,
            submission_event=EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
            autoflow_action=audit_flow.transition_to_flagged_for_removal,
        )
        return True

    elif target == STATUS.READY_FOR_CERTIFICATION:
        flow.transition_to_ready_for_certification()
        sac.save(
            event_user=user,
            event_type=SubmissionEvent.EventType.LOCKED_FOR_CERTIFICATION,
        )
        _transition_audit(
            audit=audit,
            user=user,
            submission_event=EventType.LOCKED_FOR_CERTIFICATION,
            autoflow_action=audit_flow.transition_to_ready_for_certification,
        )
        return True

    elif target == STATUS.AUDITEE_CERTIFIED:
        flow.transition_to_auditee_certified()
        sac.save(
            event_user=user,
            event_type=SubmissionEvent.EventType.AUDITEE_CERTIFICATION_COMPLETED,
        )
        _transition_audit(
            audit=audit,
            user=user,
            submission_event=EventType.AUDITEE_CERTIFICATION_COMPLETED,
            autoflow_action=audit_flow.transition_to_auditee_certified,
        )
        return True

    elif target == STATUS.AUDITOR_CERTIFIED:
        flow.transition_to_auditor_certified()
        sac.save(
            event_user=user,
            event_type=SubmissionEvent.EventType.AUDITOR_CERTIFICATION_COMPLETED,
        )
        _transition_audit(
            audit=audit,
            user=user,
            submission_event=EventType.AUDITOR_CERTIFICATION_COMPLETED,
            autoflow_action=audit_flow.transition_to_auditor_certified,
        )
        return True

    elif target == STATUS.SUBMITTED:
        flow.transition_to_submitted()
        sac.save(
            event_user=user,
            event_type=SubmissionEvent.EventType.SUBMITTED,
        )
        _transition_audit(
            audit=audit,
            user=user,
            submission_event=EventType.SUBMITTED,
            autoflow_action=audit_flow.transition_to_submitted,
        )
        return True

    elif target == STATUS.DISSEMINATED:
        flow.transition_to_disseminated()
        sac.save(
            event_user=user,
            event_type=SubmissionEvent.EventType.DISSEMINATED,
        )
        _transition_audit(
            audit=audit,
            user=user,
            submission_event=EventType.DISSEMINATED,
            autoflow_action=audit_flow.transition_to_disseminated,
        )
        return True

    return False


def _transition_audit(audit, user, submission_event, autoflow_action):
    if audit:
        autoflow_action()
        audit.save(
            event_user=user,
            event_type=submission_event,
        )


def audit_transition(request, audit, **kwargs):
    """
    Transitions the submission_state for an Audit.
    """
    user = None
    flow = AuditFlow(audit)

    target = kwargs.get("transition_to", None)

    event_to_action = {
        EventType.UNLOCKED_AFTER_CERTIFICATION: flow.transition_to_in_progress_again,
        EventType.FLAGGED_SUBMISSION_FOR_REMOVAL: flow.transition_to_flagged_for_removal,
        EventType.LOCKED_FOR_CERTIFICATION: flow.transition_to_ready_for_certification,
        EventType.AUDITEE_CERTIFICATION_COMPLETED: flow.transition_to_auditee_certified,
        EventType.AUDITOR_CERTIFICATION_COMPLETED: flow.transition_to_auditor_certified,
        EventType.SUBMITTED: flow.transition_to_submitted,
        EventType.DISSEMINATED: flow.transition_to_disseminated,
    }

    # optional - only needed when a user is involved.
    if request:
        user = request.user

    # Audit must transition to a target state.
    if target is None:
        return False

    _transition_audit(
        audit=audit,
        user=user,
        submission_event=target,
        autoflow_action=event_to_action[target],
    )
    return True


class SingleAuditChecklistFlow(SingleAuditChecklist):
    """
    Handles transitioning of states for an SAC.
    """

    state = viewflow.fsm.State(STATUS, default=STATUS.IN_PROGRESS)

    def __init__(self, sac):
        self.sac = sac

    @state.setter()
    def _set_sac_state(self, value):
        self.sac.submission_status = value

    @state.getter()
    def _get_sac_state(self):
        return self.sac.submission_status

    @state.transition(
        source=STATUS.IN_PROGRESS,
        target=STATUS.READY_FOR_CERTIFICATION,
    )
    def transition_to_ready_for_certification(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """
        self.sac.transition_name.append(STATUS.READY_FOR_CERTIFICATION)
        self.sac.transition_date.append(datetime.datetime.now(datetime.timezone.utc))

    @state.transition(
        source=[
            STATUS.IN_PROGRESS,
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.CERTIFIED,
        ],
        target=STATUS.FLAGGED_FOR_REMOVAL,
    )
    def transition_to_flagged_for_removal(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """
        self.sac.transition_name.append(STATUS.FLAGGED_FOR_REMOVAL)
        self.sac.transition_date.append(datetime.datetime.now(datetime.timezone.utc))

    @state.transition(
        source=[
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.FLAGGED_FOR_REMOVAL,
        ],
        target=STATUS.IN_PROGRESS,
    )
    def transition_to_in_progress_again(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """

        # null out any existing certifications on this submission
        self.sac.auditor_certification = None
        self.sac.auditee_certification = None

        self.sac.transition_name.append(STATUS.IN_PROGRESS)
        self.sac.transition_date.append(datetime.datetime.now(datetime.timezone.utc))

    @state.transition(
        source=STATUS.READY_FOR_CERTIFICATION,
        target=STATUS.AUDITOR_CERTIFIED,
    )
    def transition_to_auditor_certified(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """
        self.sac.transition_name.append(STATUS.AUDITOR_CERTIFIED)
        self.sac.transition_date.append(datetime.datetime.now(datetime.timezone.utc))

    @state.transition(
        source=[STATUS.AUDITOR_CERTIFIED, STATUS.SUBMITTED],
        target=STATUS.AUDITEE_CERTIFIED,
    )
    def transition_to_auditee_certified(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """
        self.sac.transition_name.append(STATUS.AUDITEE_CERTIFIED)
        self.sac.transition_date.append(datetime.datetime.now(datetime.timezone.utc))

    @state.transition(
        source=STATUS.AUDITEE_CERTIFIED,
        target=STATUS.SUBMITTED,
    )
    def transition_to_submitted(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """

        self.sac.transition_name.append(STATUS.SUBMITTED)
        self.sac.transition_date.append(datetime.datetime.now(datetime.timezone.utc))

    # WIP
    # to add - source=[STATUS.SUBMITTED, STATUS.DISSEMINATED]
    @state.transition(
        source=STATUS.SUBMITTED,
        target=STATUS.DISSEMINATED,
    )
    def transition_to_disseminated(self):
        self.sac.transition_name.append(STATUS.DISSEMINATED)
        self.sac.transition_date.append(datetime.datetime.now(datetime.timezone.utc))

    @state.transition(
        source=[
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.CERTIFIED,
        ],
        target=STATUS.AUDITEE_CERTIFIED,
    )
    def transition_to_in_progress(self):
        """
        Any edit to a submission in the following states should result in it
        moving back to STATUS.IN_PROGRESS:

        +   STATUS.READY_FOR_CERTIFICATION
        +   STATUS.AUDITOR_CERTIFIED
        +   STATUS.AUDITEE_CERTIFIED
        +   STATUS.CERTIFIED

        For the moment we're not trying anything fancy like catching changes at
        the model level, and will again leave it up to the views to track that
        changes have been made at that point.
        """
        self.sac.transition_name.append(STATUS.SUBMITTED)
        self.sac.transition_date.append(datetime.datetime.now(datetime.timezone.utc))


class AuditFlow(Audit):
    """
    Handles transitioning of states for an SAC.
    """

    state = viewflow.fsm.State(STATUS, default=STATUS.IN_PROGRESS)

    def __init__(self, audit):
        self.audit = audit

    @state.setter()
    def _set_sac_state(self, value):
        self.audit.submission_status = value

    @state.getter()
    def _get_sac_state(self):
        return self.audit.submission_status

    @state.transition(
        source=STATUS.IN_PROGRESS,
        target=STATUS.READY_FOR_CERTIFICATION,
    )
    def transition_to_ready_for_certification(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """
        pass

    @state.transition(
        source=[
            STATUS.IN_PROGRESS,
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.CERTIFIED,
        ],
        target=STATUS.FLAGGED_FOR_REMOVAL,
    )
    def transition_to_flagged_for_removal(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """
        pass

    @state.transition(
        source=[
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.FLAGGED_FOR_REMOVAL,
        ],
        target=STATUS.IN_PROGRESS,
    )
    def transition_to_in_progress_again(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """

        # null out any existing certifications on this submission
        if self.audit.audit.get("auditor_certification"):
            del self.audit.audit["auditor_certification"]
        if self.audit.audit.get("auditee_certification"):
            del self.audit.audit["auditee_certification"]

    @state.transition(
        source=STATUS.READY_FOR_CERTIFICATION,
        target=STATUS.AUDITOR_CERTIFIED,
    )
    def transition_to_auditor_certified(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """
        pass

    @state.transition(
        source=[STATUS.AUDITOR_CERTIFIED, STATUS.SUBMITTED],
        target=STATUS.AUDITEE_CERTIFIED,
    )
    def transition_to_auditee_certified(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """
        pass

    @state.transition(
        source=STATUS.AUDITEE_CERTIFIED,
        target=STATUS.SUBMITTED,
    )
    def transition_to_submitted(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will be done at the view level.
        """
        self.audit.audit.update(
            {
                "fac_accepted_date": convert_utc_to_american_samoa_zone(
                    datetime.datetime.today()
                )
            }
        )

    @state.transition(
        source=STATUS.SUBMITTED,
        target=STATUS.DISSEMINATED,
    )
    def transition_to_disseminated(self):
        """Transition to disseminated"""
        pass

    @state.transition(
        source=[
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.CERTIFIED,
        ],
        target=STATUS.AUDITEE_CERTIFIED,
    )
    def transition_to_in_progress(self):
        """
        Any edit to a submission in the following states should result in it
        moving back to STATUS.IN_PROGRESS:

        +   STATUS.READY_FOR_CERTIFICATION
        +   STATUS.AUDITOR_CERTIFIED
        +   STATUS.AUDITEE_CERTIFIED
        +   STATUS.CERTIFIED

        For the moment we're not trying anything fancy like catching changes at
        the model level, and will again leave it up to the views to track that
        changes have been made at that point.
        """
        pass
