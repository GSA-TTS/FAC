from django.db import models
from django.utils.translation import gettext_lazy as _


class SingleAuditChecklist(models.Model):
    ORGANIZATION_TYPE = (
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

    # 1. Submission criteria check -- Eligibility
    organization_type = models.CharField(max_length=12, choices=ORGANIZATION_TYPE)
    met_spending_threshold = models.BooleanField()
    is_usa_based = models.BooleanField(verbose_name=_('Is USA Based'))

    # 2 Auditee Information
    uei = models.CharField(max_length=12, verbose_name=_('UEI'), help_text=_('Unique Entity Identifier'))

    auditee_name = models.CharField(max_length=500)
    auditee_fiscal_period_start = models.DateField()
    auditee_fiscal_period_end = models.DateField()

    # General Information
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPE)
    audit_period_covered = models.CharField(max_length=20, choices=AUDIT_PERIOD)
    ein = models.CharField(max_length=12, verbose_name=_('EIN'), help_text=_('Auditee Employer Identification Number'))
    ein_not_an_ssn_attestation = models.BooleanField()
    multiple_eins_covered = models.BooleanField()
    multiple_ueis_covered = models.BooleanField()

    # Auditee Information
    auditee_name = models.CharField(max_length=100)
    auditee_address_line_1 = models.CharField(max_length=100)
    auditee_address_line_2 = models.CharField(max_length=100)
    auditee_city = models.CharField(max_length=100)
    auditee_zip = models.CharField(max_length=100)
    auditee_state = models.CharField(max_length=2)
    auditee_contact_title = models.CharField(max_length=100)
    auditee_contact_name = models.CharField(max_length=100)
    auditee_email = models.EmailField(max_length=100)
    auditee_phone = models.CharField(max_length=100)

    # Auditor Information
    auditor_name = models.CharField(max_length=100)
    auditor_ein = models.CharField(max_length=12)
    auditor_ein_not_an_ssn_attestation = models.BooleanField()
    auditor_address_line_1 = models.CharField(max_length=100)
    auditor_address_line_2 = models.CharField(max_length=100)
    auditor_city = models.CharField(max_length=100)
    auditor_zip = models.CharField(max_length=100)
    auditor_state = models.CharField(max_length=100)
    auditor_contact_title = models.CharField(max_length=100)
    auditor_contact_name = models.CharField(max_length=100)
    auditor_email = models.EmailField(max_length=100)
    auditor_phone = models.CharField(max_length=100)

    class Meta:
        verbose_name = "SF-SAC"
        verbose_name_plural = "SF-SACs"

    def __str__(self):
        return f'#{self.id} - EIN({self.ein})'
