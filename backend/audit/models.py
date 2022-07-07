from secrets import choice
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

from django.utils.translation import gettext_lazy as _

from .validators import (
    validate_uei_alphanumeric,
    validate_uei_leading_char,
    validate_uei_nine_digit_sequences,
    validate_uei_valid_chars,
)

User = get_user_model()


class SingleAuditChecklistManager(models.Manager):
    """Manager for SAC"""

    def create(self, **obj_data):
        """
        Custom create method so that we can add derived fields.

        Currently only used for report_id, a 17-character value consisting of:
            -   Four-digit year of start of audit period.
            -   Three-digit char (but without I or O) random.
            -   10-digit numeric monotonically increasing, but starting from
                0001000001 because the Census numbers are six-digit values. The
                formula for creating this is basically "how many non-legacy
                entries there are in the system plus one plus 1,000,000".


        """
        year = obj_data["auditee_fiscal_period_start"][:4]
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ1234567890"
        trichar = "".join(choice(chars) for i in range(3))
        count = SingleAuditChecklist.objects.count() + 1_000_001
        report_id = f"{year}{trichar}{str(count).zfill(10)}"
        updated = obj_data | {"report_id": report_id}
        return super().create(**updated)


class SingleAuditChecklist(models.Model):
    """
    Monolithic Single Audit Checklist.
    """

    USER_PROVIDED_ORGANIZATION_TYPE = (
        ("state", _("State")),
        ("local", _("Local Government")),
        ("tribal", _("Indian Tribe or Tribal Organization")),
        ("higher-ed", _("Institution of higher education (IHE)")),
        ("non-profit", _("Non-profit")),
        ("unknown", _("Unknown")),
        ("none", _("None of these (for example, for-profit")),
    )

    AUDIT_TYPE = (
        ("single-audit", _("Single Audit")),
        ("program-specific", _("Program-Specific Audit")),
    )

    AUDIT_PERIOD = (
        ("annual", _("Annual")),
        ("biennial", _("Biennial")),
        ("other", _("Other")),
    )
    STATUSES = (
        ("in_progress", _("In progress")),
        ("submitted", _("Submitted")),
        ("received", _("Received")),
        ("available", _("Available")),
    )

    objects = SingleAuditChecklistManager()

    # 0. Meta data
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True)
    submission_status = models.CharField(
        max_length=16, choices=STATUSES, default=STATUSES[0][0]
    )
    report_id = models.CharField(max_length=17, unique=True)

    # Part 1: General Information
    # Q1 Fiscal Dates
    auditee_fiscal_period_start = models.DateField()
    auditee_fiscal_period_end = models.DateField()

    # Q2 Type of Uniform Guidance Audit
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPE, null=True)

    # Q3 Audit Period Covered
    audit_period_covered = models.CharField(
        max_length=20, choices=AUDIT_PERIOD, null=True
    )

    # Q4 Auditee Identification Numbers
    ein = models.CharField(
        max_length=12,
        verbose_name=_("EIN"),
        help_text=_("Auditee Employer Identification Number"),
        null=True,
    )
    ein_not_an_ssn_attestation = models.BooleanField(
        verbose_name=_("Attestation: EIN Not an SSN"), null=True
    )
    multiple_eins_covered = models.BooleanField(
        verbose_name=_("Multiple EINs covered"), null=True
    )
    auditee_uei = models.CharField(
        max_length=12,
        verbose_name=_("Auditee UEI"),
        help_text=_("Auditee Unique Entity Identifier"),
        validators=[
            MinLengthValidator(12),
            validate_uei_alphanumeric,
            validate_uei_valid_chars,
            validate_uei_leading_char,
            validate_uei_nine_digit_sequences,
        ],
        blank=True,
        null=True,
    )
    multiple_ueis_covered = models.BooleanField(
        verbose_name=_("Multiple UEIs covered"), null=True
    )

    # Q5 Auditee Information
    auditee_name = models.CharField(max_length=100, null=True)
    auditee_address_line_1 = models.CharField(max_length=100, null=True)
    auditee_city = models.CharField(max_length=100, null=True)
    auditee_state = models.CharField(max_length=2, null=True)
    auditee_zip = models.CharField(max_length=100, null=True)
    auditee_contact_name = models.CharField(max_length=100, null=True)
    auditee_contact_title = models.CharField(max_length=100, null=True)
    auditee_phone = models.CharField(max_length=100, null=True)
    auditee_email = models.EmailField(max_length=100, null=True)

    # Q6 Primary Auditor Information
    user_provided_organization_type = models.CharField(
        max_length=12, choices=USER_PROVIDED_ORGANIZATION_TYPE
    )
    met_spending_threshold = models.BooleanField()
    is_usa_based = models.BooleanField(verbose_name=_("Is USA Based"))
    auditor_firm_name = models.CharField(max_length=100, null=True)
    auditor_ein = models.CharField(
        max_length=12, verbose_name=_("Auditor EIN"), null=True
    )
    auditor_ein_not_an_ssn_attestation = models.BooleanField(
        verbose_name=_("Attestation: Auditor EIN Not an SSN"), null=True
    )
    auditor_country = models.CharField(max_length=100, null=True)
    auditor_address_line_1 = models.CharField(max_length=100, null=True)
    auditor_city = models.CharField(max_length=100, null=True)
    auditor_state = models.CharField(max_length=100, null=True)
    auditor_zip = models.CharField(max_length=100, null=True)
    auditor_contact_name = models.CharField(max_length=100, null=True)
    auditor_contact_title = models.CharField(max_length=100, null=True)
    auditor_phone = models.CharField(max_length=100, null=True)
    auditor_email = models.EmailField(max_length=100, null=True)

    class Meta:
        verbose_name = "SF-SAC"
        verbose_name_plural = "SF-SACs"

    def __str__(self):
        return f"#{self.id} - UEI({self.auditee_uei})"


class Access(models.Model):
    """
    Email addresses which have been granted access to SAC instances.
    An email address may be associated with a User ID if an FAC account exists.
    """

    ROLES = (
        ("auditee_contact", _("Auditee Contact")),
        ("auditee_cert", _("Auditee Certifying Official")),
        ("auditor_contact", _("Auditor Contact")),
        ("auditor_cert", _("Auditor Certifying Official")),
    )
    sac = models.ForeignKey(
        SingleAuditChecklist, related_name="users", on_delete=models.PROTECT
    )
    role = models.CharField(
        choices=ROLES,
        help_text="Access type granted to this user",
        max_length=15,
    )
    email = models.EmailField()
    user_id = models.ForeignKey(
        User,
        null=True,
        help_text="User ID associated with this email address, empty if no FAC account exists",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.email} as {self.role} for {self.sac}"
