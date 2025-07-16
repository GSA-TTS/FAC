BIGINT_MAX_DIGITS = 25

REPORT_ID_FK_HELP_TEXT = "GSAFAC generated identifier"


class RESUBMISSION_STATUS:
    """
    The possible states of a resubmission.
    """

    ORIGINAL_SUBMISSION = "Original Submission"
    MOST_RECENT = "Most Recent"
    DEPRECATED_VIA_RESUBMISSION = "Depracated via Resubmission"


RESUBMISSION_STATUS_CHOICES = (
    (RESUBMISSION_STATUS.ORIGINAL_SUBMISSION, "Original Submission"),
    (RESUBMISSION_STATUS.MOST_RECENT, "Most Recent"),
    (RESUBMISSION_STATUS.DEPRECATED_VIA_RESUBMISSION, "Depracated via Resubmission"),
)
