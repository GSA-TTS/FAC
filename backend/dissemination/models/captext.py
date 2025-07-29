from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT
from dissemination.models import docs


class CapText(models.Model):
    """Corrective action plan text. Referebces General"""

    contains_chart_or_table = models.TextField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        help_text=docs.charts_tables_captext,
    )
    finding_ref_number = models.TextField(
        "Audit Finding Reference Number",
        help_text=docs.finding_ref_nums_captext,
    )
    planned_action = models.TextField(
        "Content of the Corrective Action Plan (CAP)",
        help_text=docs.text_captext,
    )
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
