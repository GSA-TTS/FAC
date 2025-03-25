import logging

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone as django_timezone
from .utils import one_month_from_today

User = get_user_model()

logger = logging.getLogger(__name__)


class UeiValidationWaiver(models.Model):
    """Records of UEIs that are permitted to be inactive."""

    # Method overrides:
    def __str__(self):
        return f"#{self.id}--{self.uei}"

    # Not unique, in the case that one UEI needs to be waived several times with different expiration dates.
    uei = models.TextField("UEI")
    timestamp = models.DateTimeField(
        "When the waiver was created",
        default=django_timezone.now,
    )
    expiration = models.DateTimeField(
        "When the waiver will expire",
        default=one_month_from_today,
    )
    approver_email = models.TextField(
        "Email address of FAC staff member approving the waiver",
    )
    approver_name = models.TextField(
        "Name of FAC staff member approving the waiver",
    )
    requester_email = models.TextField(
        "Email address of NSAC/KSAML requesting the waiver",
    )
    requester_name = models.TextField(
        "Name of NSAC/KSAML requesting the waiver",
    )
    justification = models.TextField(
        "Brief plain-text justification for the waiver",
    )


class SacValidationWaiver(models.Model):
    """Records of reports that have had a requirement waived."""

    class TYPES:
        AUDITEE_CERTIFYING_OFFICIAL = "auditee_certifying_official"
        AUDITOR_CERTIFYING_OFFICIAL = "auditor_certifying_official"
        FINDING_REFERENCE_NUMBER = "finding_reference_number"
        PRIOR_REFERENCES = "prior_references"

    WAIVER_CHOICES = [
        (
            TYPES.AUDITEE_CERTIFYING_OFFICIAL,
            "No auditee certifying official is available",
        ),
        (
            TYPES.AUDITOR_CERTIFYING_OFFICIAL,
            "No auditor certifying official is available",
        ),
        (
            TYPES.FINDING_REFERENCE_NUMBER,
            "Report has duplicate finding reference numbers",
        ),
        (
            TYPES.PRIOR_REFERENCES,
            "Report has invalid prior reference numbers",
        ),
    ]
    report_id = models.ForeignKey(
        "SingleAuditChecklist",
        help_text="The report that the waiver applies to",
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    timestamp = models.DateTimeField(
        "When the waiver was created",
        default=django_timezone.now,
    )
    approver_email = models.TextField(
        "Email address of FAC staff member approving the waiver",
    )
    approver_name = models.TextField(
        "Name of FAC staff member approving the waiver",
    )
    requester_email = models.TextField(
        "Email address of NSAC/KSAML requesting the waiver",
    )
    requester_name = models.TextField(
        "Name of NSAC/KSAML requesting the waiver",
    )
    justification = models.TextField(
        "Brief plain-text justification for the waiver",
    )
    waiver_types = ArrayField(
        models.CharField(
            max_length=50,
            choices=WAIVER_CHOICES,
        ),
        verbose_name="The waiver type",
        default=list,
    )
