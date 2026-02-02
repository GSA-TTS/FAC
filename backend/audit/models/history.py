from django.contrib.auth import get_user_model
from django.db import models

from audit.models.constants import EVENT_TYPES

User = get_user_model()


class History(models.Model):
    """
    Represents a history of the audit. Contains the audit json object at the time
    of the event.
    """

    event = models.CharField(choices=EVENT_TYPES)
    report_id = models.CharField()
    version = models.IntegerField()
    event_data = models.JSONField()
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT)

    fake_field = models.TextField(
        null=True,
    )

    class Meta:
        verbose_name = "Audit History"
        verbose_name_plural = "Audit History"
