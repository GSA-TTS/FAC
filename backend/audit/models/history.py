from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class History(models.Model):
    """
    Represents a history of the audit. Contains the audit json object at the time
    of the event.
    """
    event = models.CharField(choices=[]) # TODO Define Events
    report_id = models.CharField() # TODO Define
    version = models.IntegerField()
    audit = models.JSONField()
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT)
