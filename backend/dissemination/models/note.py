from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT
from dissemination.models import docs


class Note(models.Model):
    """Note to Schedule of Expenditures of Federal Awards (SEFA)"""

    HASH_FIELDS = [
        "id",
        "report_id",
        "note_title",
        "accounting_policies",
        "rate_explained",
        "is_minimis_rate_used",
        "content",
        "contains_chart_or_table",
    ]

    accounting_policies = models.TextField(
        "A description of the significant accounting policies used in preparing the SEFA (2 CFR 200.510(b)(6))",
    )
    is_minimis_rate_used = models.TextField("'Yes', 'No', or 'Both' (2 CFR 200.414(f))")
    rate_explained = models.TextField("Explanation for minimis rate")
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    content = models.TextField("Content of the Note", help_text=docs.content)
    note_title = models.TextField("Note title", help_text=docs.title)
    contains_chart_or_table = models.TextField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        help_text=docs.charts_tables_note,
    )
    hash = models.CharField(
        help_text="A hash of the row",
        blank=True,
        null=True,
    )
