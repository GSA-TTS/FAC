from django.db import models

from audit.models.constants import RESUBMISSION_STATUS_CHOICES
from .constants import REPORT_ID_FK_HELP_TEXT

# from dissemination.models import docs


class Resubmission(models.Model):
    """
    Resubmission metadata. Contains info on the specified record, and links to the previous
    and next versions, if they exist. No default values - all fields are assumed to be filled or NULL.
    """

    # Foreign key links to all the other parts of the record. Unique in this table.
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )

    # Required to be non-null.
    version = models.BigIntegerField(
        "Resubmission Version",
        # help_text=docs.resubmission_version,  # "Original submissions/most recent are version 1. Subsequent resubmissions increment the value."
    )
    status = models.CharField(
        "Resubmission Status (Unknown, Deprecated, Resubmission)",
        max_length=30,
        choices=RESUBMISSION_STATUS_CHOICES,
        # help_text=docs.resubmission_status,  # "The resubmission status of this record. Displays whether it is a singular most recent, a resubmission, or a previous version."
    )

    # Allowed to be null
    previous_report_id = models.TextField(
        "Previous Report ID",
        # help_text=docs.previous_report_id,  # "The report_id of the previous version. Points back to a deprecated record."
        null=True,
    )
    next_report_id = models.TextField(
        "Next Report ID",
        # help_text=docs.next_report_id,  # "The report_id of the next version. Points up the chain from a deprecated record."
        null=True,
    )

    # Eventually:
    # resubmission_justification. Either a TextField provided by the user, or a CharField with choices for predetermined justifications.
    # changed_fields. A TextField with a string of comma separated field names. i.e. "one_field, two_field, red_field, blue_field".

    def __str__(self):
        return f"report_id:{self.report_id} Version:{self.resubmission_version}, Status:{self.resubmission_status}"
