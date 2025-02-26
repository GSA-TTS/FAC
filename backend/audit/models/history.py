from django.contrib.auth import get_user_model
from django.db import models

from audit.models.constants import STATUS_CHOICES

User = get_user_model()


class History(models.Model):
    """
    Represents a history of the audit. Contains the audit json object at the time
    of the event.
    """

    event = models.CharField(choices=STATUS_CHOICES)
    report_id = models.CharField()
    version = models.IntegerField()
    audit = models.JSONField()
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT)
