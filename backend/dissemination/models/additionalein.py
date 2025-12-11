from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT


class AdditionalEin(models.Model):
    """Additional EINs for this audit."""

    HASH_FIELDS = ["report_id", "additional_ein"]

    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    additional_ein = models.TextField()
    hash = models.CharField(
        help_text="A hash of the row",
        blank=True,
        null=True,
    )
