from django.db import models


BIGINT_MAX_DIGITS = 25

REPORT_ID_FK_HELP_TEXT = "GSAFAC generated identifier"


class ResubmissionStatus(models.TextChoices):
    ORIGINAL = "original_submission", "Original Submission"
    MOST_RECENT = "most_recent", "Most Recent"
    DEPRECATED = "deprecated_via_resubmission", "Deprecated via Resubmission"
