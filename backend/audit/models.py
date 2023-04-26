from secrets import choice
from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _

from .validators import (
    validate_excel_file,
    validate_excel_filename,
    validate_corrective_action_plan_json,
    validate_federal_award_json,
    validate_findings_text_json,
    validate_findings_uniform_guidance_json,
    validate_general_information_json,
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
        year = obj_data["general_information"]["auditee_fiscal_period_start"][:4]
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ1234567890"
        trichar = "".join(choice(chars) for _ in range(3))
        count = SingleAuditChecklist.objects.count() + 1_000_001
        report_id = f"{year}{trichar}{str(count).zfill(10)}"
        updated = obj_data | {"report_id": report_id}
        return super().create(**updated)


class SingleAuditChecklist(models.Model):
    """
    Monolithic Single Audit Checklist.
    """

    USER_PROVIDED_ORGANIZATION_TYPE_CODE = (
        ("state", _("State")),
        ("local", _("Local Government")),
        ("tribal", _("Indian Tribe or Tribal Organization")),
        ("higher-ed", _("Institution of higher education (IHE)")),
        ("non-profit", _("Non-profit")),
        ("unknown", _("Unknown")),
        ("none", _("None of these (for example, for-profit")),
    )

    AUDIT_TYPE_CODES = (
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

    # Q2 Type of Uniform Guidance Audit
    audit_type = models.CharField(
        max_length=20, choices=AUDIT_TYPE_CODES, blank=True, null=True
    )

    # General Information
    # The general information fields are currently specified in two places:
    #   - report_submission.forms.GeneralInformationForm
    #   - schemas.sections.GeneralInformation.schema.json
    general_information = models.JSONField(
        blank=True, null=True, validators=[validate_general_information_json]
    )

    # Federal Awards:
    federal_awards = models.JSONField(
        blank=True, null=True, validators=[validate_federal_award_json]
    )

    # Corrective Action Plan:
    corrective_action_plan = models.JSONField(
        blank=True, null=True, validators=[validate_corrective_action_plan_json]
    )

    # Findings Text:
    findings_text = models.JSONField(
        blank=True, null=True, validators=[validate_findings_text_json]
    )

    # Findings Uniform Guidance:
    findings_uniform_guidance = models.JSONField(
        blank=True, null=True, validators=[validate_findings_uniform_guidance_json]
    )

    @property
    def audit_period_covered(self):
        return self._general_info_get("audit_period_covered")

    @property
    def auditee_uei(self):
        return self._general_info_get("auditee_uei")

    @property
    def auditee_fiscal_period_end(self):
        return self._general_info_get("auditee_fiscal_period_end")

    @property
    def auditee_fiscal_period_start(self):
        return self._general_info_get("auditee_fiscal_period_start")

    @property
    def auditee_name(self):
        return self._general_info_get("auditee_name")

    @property
    def auditee_email(self):
        return self._general_info_get("auditee_email")

    @property
    def auditor_email(self):
        return self._general_info_get("auditor_email")

    @property
    def auditee_phone(self):
        return self._general_info_get("auditee_phone")

    @property
    def is_usa_based(self):
        return self._general_info_get("is_usa_based")

    @property
    def met_spending_threshold(self):
        return self._general_info_get("met_spending_threshold")

    @property
    def user_provided_organization_type(self):
        return self._general_info_get("user_provided_organization_type")

    @property
    def ein(self):
        return self._general_info_get("ein")

    @property
    def ein_not_an_ssn_attestation(self):
        return self._general_info_get("ein_not_an_ssn_attestation")

    @property
    def multiple_eins_covered(self):
        return self._general_info_get("multiple_eins_covered")

    @property
    def multiple_ueis_covered(self):
        return self._general_info_get("multiple_ueis_covered")

    @property
    def auditee_address_line_1(self):
        return self._general_info_get("auditee_address_line_1")

    @property
    def auditee_city(self):
        return self._general_info_get("auditee_city")

    @property
    def auditee_state(self):
        return self._general_info_get("auditee_state")

    @property
    def auditee_zip(self):
        return self._general_info_get("auditee_zip")

    @property
    def auditee_contact_name(self):
        return self._general_info_get("auditee_contact_name")

    @property
    def auditee_contact_title(self):
        return self._general_info_get("auditee_contact_title")

    @property
    def auditor_firm_name(self):
        return self._general_info_get("auditor_firm_name")

    @property
    def auditor_ein(self):
        return self._general_info_get("auditor_ein")

    @property
    def auditor_ein_not_an_ssn_attestation(self):
        return self._general_info_get("auditor_ein_not_an_ssn_attestation")

    @property
    def auditor_country(self):
        return self._general_info_get("auditor_country")

    @property
    def auditor_address_line_1(self):
        return self._general_info_get("auditor_address_line_1")

    @property
    def auditor_city(self):
        return self._general_info_get("auditor_city")

    @property
    def auditor_state(self):
        return self._general_info_get("auditor_state")

    @property
    def auditor_zip(self):
        return self._general_info_get("auditor_zip")

    @property
    def auditor_contact_name(self):
        return self._general_info_get("auditor_contact_name")

    @property
    def auditor_contact_title(self):
        return self._general_info_get("auditor_contact_title")

    @property
    def auditor_phone(self):
        return self._general_info_get("auditor_phone")

    def _general_info_get(self, key):
        try:
            return self.general_information[key]
        except KeyError:
            pass
        except TypeError:
            pass
        return None

    class Meta:
        """We need to set the name for the admin view."""

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
        ("auditor_contact", _("Auditor Contact")),
        ("certifying_auditee_contact ", _("Auditee Certifying Official")),
        ("certifying_auditor_contact ", _("Auditor Certifying Official")),
        ("creator", _("Audit Creator")),
    )
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    role = models.CharField(
        choices=ROLES,
        help_text="Access type granted to this user",
        max_length=50,
    )
    email = models.EmailField()
    user = models.ForeignKey(
        User,
        null=True,
        help_text="User ID associated with this email address, empty if no FAC account exists",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.email} as {self.get_role_display()}"

    class Meta:
        verbose_name_plural = "accesses"

        constraints = [
            # a SAC cannot have multiple creators
            models.UniqueConstraint(
                fields=["sac"],
                condition=Q(role="creator"),
                name="%(app_label)s_$(class)s_single_creator",
            ),
            # a SAC cannot have multiple certifying auditees
            models.UniqueConstraint(
                fields=["sac"],
                condition=Q(role="certifying_auditee_contact"),
                name="%(app_label)s_$(class)s_single_certifying_auditee",
            ),
            # a SAC cannot have multiple certifying auditors
            models.UniqueConstraint(
                fields=["sac"],
                condition=Q(role="certifying_auditor_contact"),
                name="%(app_label)s_%(class)s_single_certifying_auditor",
            ),
        ]


class ExcelFile(models.Model):
    """
    Data model to track uploaded Excel files and associate them with SingleAuditChecklists
    """

    file = models.FileField(upload_to="excel", validators=[validate_excel_file])
    filename = models.CharField(max_length=255)
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.filename = validate_excel_filename(self.file)
        super(ExcelFile, self).save(*args, **kwargs)
