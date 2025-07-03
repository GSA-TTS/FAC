from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT


class TribalApiAccessKeyIds(models.Model):
    email = models.TextField(
        "Email of the user",
        unique=True,
    )
    key_id = models.TextField(
        "Key ID for the api access",
    )
    date_added = models.DateField(
        "Added date of the record",
    )
