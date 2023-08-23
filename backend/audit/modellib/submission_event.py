from enum import Enum

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from audit.models import SingleAuditChecklist

User = get_user_model()


class EventType(Enum):
    ADDITIONAL_EINS_UPDATED = "additional-ueis-updated"
    CREATED = "created"


EVENT_TYPES = (
    (EventType.ADDITIONAL_EINS_UPDATED, _("Additional EINs updated")),
    ("additional-ueis-updated", _("Additional UEIs updated")),
    ("audit-information-updated", _("Audit information updated")),
    ("audit-report-pdf-updated", _("Audit report PDF updated")),
    ("auditee-certification-completed", _("Auditee certification completed")),
    ("auditor-certification-completed", _("Auditor certification completed")),
    ("corrective-action-plan-updated", _("Corrective action plan updated")),
    (EventType.CREATED, _("Created")),
    ("federal-awards-updated", _("Federal awards updated")),
    ("federal-awards-audit-findings-updated", _("Federal awards audit findings updated")),
    ("federal-awards-audit-findings-text-updated", _("Federal awards audit findings text updated")),
    ("findings-uniform-guidance-updated", _("Findings uniform guidance updated")),
    ("general-information-updated", _("General information updated")),
    ("locked-for-certification", _("Locked for certification")),
    ("notes-to-sefa-updated", _("Notes to SEFA updated")),
    ("secondary-auditors-updated", _("Secondary auditors updated")),
    ("submitted", _("Submitted to the FAC for processing")),
)


class SubmissionEvent(models.Model):
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.CharField(choices=EVENT_TYPES)
