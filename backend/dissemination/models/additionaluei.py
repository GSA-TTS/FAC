from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT


class AdditionalUei(models.Model):
    """Additional UEIs for this audit."""

    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    additional_uei = models.TextField()
