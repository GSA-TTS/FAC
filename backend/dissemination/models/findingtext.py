from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT
from dissemination.models import docs


class FindingText(models.Model):
    """Specific findings details. References General"""

    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    finding_ref_number = models.TextField(
        "Finding Reference Number - FK",
        help_text=docs.finding_ref_nums_findingstext,
    )
    contains_chart_or_table = models.TextField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        help_text=docs.charts_tables_findingstext,
    )
    finding_text = models.TextField(
        "Content of the finding text",
        help_text=docs.text_findingstext,
    )
