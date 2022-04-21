from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

from django.utils.translation import gettext_lazy as _

from .validators import validate_uei_alphanumeric, validate_uei_leading_char, validate_uei_nine_digit_sequences, validate_uei_valid_chars

User = get_user_model()


class SingleAuditChecklist(models.Model):
    USER_PROVIDED_ORGANIZATION_TYPE = (
        ('state', _('State')),
        ('local', _('Local Government')),
        ('tribal', _('Indian Tribe or Tribal Organization')),
        ('non-profit', _('Non-profit')),
        ('unknown', _('Unknown')),
        ('none', _("None of these (for example, for-profit")),
    )

    AUDIT_TYPE = (
        ('single-audit', _('Single Audit')),
        ('program-specific', _('Program-Specific Audit')),
    )

    AUDIT_PERIOD = (
        ('annual', _('Annual')),
        ('biennial', _('Biennial')),
        ('other', _('Other')),
    )

    # 0. Meta data
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True)

    # 1. Submission criteria check -- Eligibility
    user_provided_organization_type = models.CharField(max_length=12, choices=USER_PROVIDED_ORGANIZATION_TYPE)
    met_spending_threshold = models.BooleanField()
    is_usa_based = models.BooleanField(verbose_name=_('Is USA Based'))

    # 2 Auditee Information
    uei = models.CharField(max_length=12, verbose_name=_('UEI'), help_text=_('Unique Entity Identifier'), validators=[MinLengthValidator(12), validate_uei_alphanumeric, validate_uei_valid_chars, validate_uei_leading_char, validate_uei_nine_digit_sequences])

    auditee_name = models.CharField(max_length=500)
    auditee_fiscal_period_start = models.DateField()
    auditee_fiscal_period_end = models.DateField()

    # General Information
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPE, null=True)
    audit_period_covered = models.CharField(max_length=20, choices=AUDIT_PERIOD, null=True)
    ein = models.CharField(max_length=12, verbose_name=_('EIN'), help_text=_('Auditee Employer Identification Number'), null=True)
    ein_not_an_ssn_attestation = models.BooleanField(verbose_name=_('Attestation: EIN Not an SSN'), null=True)
    multiple_eins_covered = models.BooleanField(verbose_name=_('Multiple EINs covered'), null=True)
    multiple_ueis_covered = models.BooleanField(verbose_name=_('Multiple UEIs covered'), null=True)

    # Auditee Information
    auditee_name = models.CharField(max_length=100, null=True)
    auditee_address_line_1 = models.CharField(max_length=100, null=True)
    auditee_address_line_2 = models.CharField(max_length=100, null=True)
    auditee_city = models.CharField(max_length=100, null=True)
    auditee_zip = models.CharField(max_length=100, null=True)
    auditee_state = models.CharField(max_length=2, null=True)
    auditee_contact_title = models.CharField(max_length=100, null=True)
    auditee_contact_name = models.CharField(max_length=100, null=True)
    auditee_email = models.EmailField(max_length=100, null=True)
    auditee_phone = models.CharField(max_length=100, null=True)

    # Auditor Information
    auditor_name = models.CharField(max_length=100, null=True)
    auditor_ein = models.CharField(max_length=12, verbose_name=_('Auditor EIN'), null=True)
    auditor_ein_not_an_ssn_attestation = models.BooleanField(verbose_name=_('Attestation: Auditor EIN Not an SSN'), null=True)
    auditor_address_line_1 = models.CharField(max_length=100, null=True)
    auditor_address_line_2 = models.CharField(max_length=100, null=True)
    auditor_city = models.CharField(max_length=100, null=True)
    auditor_zip = models.CharField(max_length=100, null=True)
    auditor_state = models.CharField(max_length=100, null=True)
    auditor_contact_title = models.CharField(max_length=100, null=True)
    auditor_contact_name = models.CharField(max_length=100, null=True)
    auditor_email = models.EmailField(max_length=100, null=True)
    auditor_phone = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = "SF-SAC"
        verbose_name_plural = "SF-SACs"

    def __str__(self):
        return f'#{self.id} - EIN({self.ein})'
