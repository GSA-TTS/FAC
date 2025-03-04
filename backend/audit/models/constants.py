from django.utils.translation import gettext_lazy as _


class STATUS:
    """
    The possible states of a submission.
    """

    IN_PROGRESS = "in_progress"
    READY_FOR_CERTIFICATION = "ready_for_certification"
    AUDITOR_CERTIFIED = "auditor_certified"
    AUDITEE_CERTIFIED = "auditee_certified"
    CERTIFIED = "certified"
    SUBMITTED = "submitted"
    DISSEMINATED = "disseminated"
    FLAGGED_FOR_REMOVAL = "flagged_for_removal"


STATUS_CHOICES = (
    (STATUS.IN_PROGRESS, "In Progress"),
    (STATUS.FLAGGED_FOR_REMOVAL, "Flagged for Removal"),
    (STATUS.READY_FOR_CERTIFICATION, "Ready for Certification"),
    (STATUS.AUDITOR_CERTIFIED, "Auditor Certified"),
    (STATUS.AUDITEE_CERTIFIED, "Auditee Certified"),
    (STATUS.CERTIFIED, "Certified"),
    (STATUS.SUBMITTED, "Submitted"),
    (STATUS.DISSEMINATED, "Disseminated"),
)


class AuditType:
    SINGLE_AUDIT = "single_audit"
    PROGRAM_SPECIFIC = "program_specific"


AUDIT_TYPE_CODES = (
    (AuditType.SINGLE_AUDIT, _("Single Audit")),
    (AuditType.PROGRAM_SPECIFIC, _("Program-Specific Audit")),
)
