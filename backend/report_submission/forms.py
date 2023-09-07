from django import forms
from config.settings import STATE_ABBREVS

from api.uei import get_uei_info_from_sam_gov


def validate_uei(value):
    sam_response = get_uei_info_from_sam_gov(value)
    if sam_response.get("errors"):
        raise forms.ValidationError(sam_response.get("errors"))


class AuditeeInfoForm(forms.Form):
    auditee_uei = forms.CharField(required=True, validators=[validate_uei])
    auditee_fiscal_period_start = forms.DateField(required=True)
    auditee_fiscal_period_end = forms.DateField(required=True)

    def clean(self):
        if self.is_valid():
            cleaned_data = super().clean()

            auditee_fiscal_period_start = cleaned_data["auditee_fiscal_period_start"]
            auditee_fiscal_period_end = cleaned_data["auditee_fiscal_period_end"]

            if auditee_fiscal_period_start >= auditee_fiscal_period_end:
                raise forms.ValidationError(
                    "Auditee fiscal period end date must be later than auditee fiscal period start date"
                )


# The general information fields are currently specified in two places:
#   - report_submission.forms.GeneralInformationForm
#   - schemas.sections.GeneralInformation.schema.json


class GeneralInformationForm(forms.Form):
    choices_state_abbrevs = list((i, i) for i in STATE_ABBREVS)

    audit_type = forms.CharField()
    auditee_fiscal_period_end = forms.CharField()
    auditee_fiscal_period_start = forms.CharField()
    audit_period_covered = forms.CharField()
    audit_period_other_months = forms.CharField(required=False)
    ein = forms.CharField()
    ein_not_an_ssn_attestation = forms.BooleanField(required=False)
    multiple_eins_covered = forms.BooleanField(required=False)
    auditee_uei = forms.CharField()
    multiple_ueis_covered = forms.BooleanField(required=False)
    auditee_name = forms.CharField()
    auditee_address_line_1 = forms.CharField()
    auditee_city = forms.CharField()
    auditee_state = forms.ChoiceField(choices=choices_state_abbrevs)
    auditee_zip = forms.CharField()
    auditee_contact_name = forms.CharField()
    auditee_contact_title = forms.CharField()
    auditee_phone = forms.CharField()
    auditee_email = forms.CharField()
    auditor_firm_name = forms.CharField()
    auditor_ein = forms.CharField()
    auditor_ein_not_an_ssn_attestation = forms.BooleanField(required=False)
    auditor_country = forms.CharField()
    auditor_international_address = forms.CharField(required=False)
    auditor_address_line_1 = forms.CharField(required=False)
    auditor_city = forms.CharField(required=False)
    auditor_state = forms.CharField(required=False)
    auditor_zip = forms.CharField(required=False)
    auditor_contact_name = forms.CharField()
    auditor_contact_title = forms.CharField()
    auditor_phone = forms.CharField()
    auditor_email = forms.CharField()
    secondary_auditors_exist = forms.BooleanField(required=False)
