from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT
from dissemination.models import docs


class Passthrough(models.Model):
    """The pass-through entity information, when it is not a direct federal award"""

    award_reference = models.TextField(
        "Order that the award line was reported",
    )
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    passthrough_id = models.TextField(
        "Identifying Number Assigned by the Pass-through Entity",
        help_text=docs.passthrough_id,
    )
    passthrough_name = models.TextField(
        "Name of Pass-through Entity",
        help_text=docs.passthrough_name,
    )
