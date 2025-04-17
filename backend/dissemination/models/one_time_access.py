from django.db import models

REPORT_ID_FK_HELP_TEXT = "GSAFAC generated identifier"


class OneTimeAccess(models.Model):
    uuid = models.UUIDField()
    timestamp = models.DateTimeField(
        auto_now_add=True,
    )
    api_key_id = models.TextField(
        "API key Id for the user",
    )
    report_id = models.TextField(
        "Report ID",
        help_text=REPORT_ID_FK_HELP_TEXT,
    )
