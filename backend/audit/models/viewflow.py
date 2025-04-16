from audit.models import Audit
from audit.models.constants import EventType, STATUS
from audit.models.utils import convert_utc_to_american_samoa_zone
from curation.curationlib.curation_audit_tracking import CurationTracking
import datetime
import logging
import viewflow.fsm

logger = logging.getLogger(__name__)


def audit_revert_from_submitted(audit):
    """
    Transitions the submission_state for an Audit back
    to "auditee_certified" so the user can re-address issues and submit.
    This should only be executed via management command.
    """

    if audit.submission_status == STATUS.SUBMITTED:
        flow = AuditFlow(audit)

        flow.transition_to_auditee_certified()

        with CurationTracking():
            audit.save(
                event_user=None,
                event_type=EventType.AUDITEE_CERTIFICATION_COMPLETED,
            )
        return True
    return False


def audit_revert_from_flagged_for_removal(audit, user):
    """
    Transitions the submission_state for an Audit back
    to "in_progress" so the user can continue working on it.
    This should be accessible to django admin.
    """
    flow = AuditFlow(audit)

    flow.transition_to_in_progress_again()

    with CurationTracking():
        audit.save(
            event_user=user,
            event_type=EventType.CANCEL_REMOVAL_FLAG,
        )


def audit_flag_for_removal(audit, user):
    """
    Transitions the submission_state for an Audit to "flagged_for_removal".
    This should be accessible to django admin.
    """
    if audit.submission_status == STATUS.IN_PROGRESS:
        flow = AuditFlow(audit)
        flow.transition_to_flagged_for_removal()
        with CurationTracking():
            audit.save(
                event_user=user,
                event_type=EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
            )


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

    target = kwargs.get("event", None)

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
