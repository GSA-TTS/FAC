import logging
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class AdminApiEvent(models.Model):
    class EventType:
        TRIBAL_ACCESS_EMAIL_ADDED = "tribal-access-email-added"
        TRIBAL_ACCESS_EMAIL_REMOVED = "tribal-access-email-removed"

    EVENT_TYPES = (
        (EventType.TRIBAL_ACCESS_EMAIL_ADDED, _("Tribal access granted")),
        (EventType.TRIBAL_ACCESS_EMAIL_REMOVED, _("Trbial access removed")),
    )

    # sac = models.ForeignKey("audit.SingleAuditChecklist", on_delete=models.CASCADE)
    # user = models.ForeignKey(User, on_delete=models.PROTECT)
    api_key_uuid = models.TextField()
    event = models.CharField(choices=EVENT_TYPES)
    event_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
