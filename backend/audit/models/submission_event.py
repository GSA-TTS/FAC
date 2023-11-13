import logging
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()

logger = logging.getLogger(__name__)


class SubmissionEvent(models.Model):
    class EventType:
        ACCESS_GRANTED = "access-granted"
        ADDITIONAL_EINS_UPDATED = "additional-eins-updated"
        ADDITIONAL_UEIS_UPDATED = "additional-ueis-updated"
        AUDIT_INFORMATION_UPDATED = "audit-information-updated"
        AUDIT_REPORT_PDF_UPDATED = "audit-report-pdf-updated"
        AUDITEE_CERTIFICATION_COMPLETED = "auditee-certification-completed"
        AUDITOR_CERTIFICATION_COMPLETED = "auditor-certification-completed"
        CORRECTIVE_ACTION_PLAN_UPDATED = "corrective-action-plan-updated"
        CREATED = "created"
        FEDERAL_AWARDS_UPDATED = "federal-awards-updated"
        FEDERAL_AWARDS_AUDIT_FINDINGS_UPDATED = "federal-awards-audit-findings-updated"
        FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_UPDATED = (
            "federal-awards-audit-findings-text-updated"
        )
        FINDINGS_UNIFORM_GUIDANCE_UPDATED = "findings-uniform-guidance-updated"
        GENERAL_INFORMATION_UPDATED = "general-information-updated"
        LOCKED_FOR_CERTIFICATION = "locked-for-certification"
        UNLOCKED_AFTER_CERTIFICATION = "unlocked-after-certification"
        NOTES_TO_SEFA_UPDATED = "notes-to-sefa-updated"
        SECONDARY_AUDITORS_UPDATED = "secondary-auditors-updated"
        SUBMITTED = "submitted"
        DISSEMINATED = "disseminated"
        TRIBAL_CONSENT_UPDATED = "tribal-consent-updated"

    EVENT_TYPES = (
        (EventType.ACCESS_GRANTED, _("Access granted")),
        (EventType.ADDITIONAL_EINS_UPDATED, _("Additional EINs updated")),
        (EventType.ADDITIONAL_UEIS_UPDATED, _("Additional UEIs updated")),
        (EventType.AUDIT_INFORMATION_UPDATED, _("Audit information updated")),
        (EventType.AUDIT_REPORT_PDF_UPDATED, _("Audit report PDF updated")),
        (
            EventType.AUDITEE_CERTIFICATION_COMPLETED,
            _("Auditee certification completed"),
        ),
        (
            EventType.AUDITOR_CERTIFICATION_COMPLETED,
            _("Auditor certification completed"),
        ),
        (EventType.CORRECTIVE_ACTION_PLAN_UPDATED, _("Corrective action plan updated")),
        (EventType.CREATED, _("Created")),
        (EventType.FEDERAL_AWARDS_UPDATED, _("Federal awards updated")),
        (
            EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_UPDATED,
            _("Federal awards audit findings updated"),
        ),
        (
            EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_UPDATED,
            _("Federal awards audit findings text updated"),
        ),
        (
            EventType.FINDINGS_UNIFORM_GUIDANCE_UPDATED,
            _("Findings uniform guidance updated"),
        ),
        (EventType.GENERAL_INFORMATION_UPDATED, _("General information updated")),
        (EventType.LOCKED_FOR_CERTIFICATION, _("Locked for certification")),
        (EventType.UNLOCKED_AFTER_CERTIFICATION, _("Unlocked after certification")),
        (EventType.NOTES_TO_SEFA_UPDATED, _("Notes to SEFA updated")),
        (EventType.SECONDARY_AUDITORS_UPDATED, _("Secondary auditors updated")),
        (EventType.SUBMITTED, _("Submitted to the FAC for processing")),
        (EventType.DISSEMINATED, _("Copied to dissemination tables")),
        (EventType.TRIBAL_CONSENT_UPDATED, _("Tribal audit consent updated")),
    )

    sac = models.ForeignKey("audit.SingleAuditChecklist", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.CharField(choices=EVENT_TYPES)
