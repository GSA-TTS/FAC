from django import forms
from django.core.validators import RegexValidator

from api.uei import get_uei_info_from_sam_gov

ein_validator = RegexValidator(r'^[0-9]{9}$', "EINs should be nine characters long and be made up of only numbers.")
# Regex for words, includes non-[A-Z] ASCII characters like ñ and ī.
# \A and \Z start and terminate the string.
# [^\W\d] - matches values _not_ in W (non-word characters) or d (digits), which is all alphas.
# [^\W\d] is OR'd with \s to allow whitespace instead of another character, to allow spaces.
# [^\W\d]|\s is wrapped in parenthesis and appended by a plus to allow any number of characters.
alpha_validator = RegexValidator(r'\A([^\W\d]|\s)+\Z', "This field should not include numbers or special characters.")


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
    audit_type = forms.CharField(required=False)
    auditee_fiscal_period_end = forms.CharField(required=False)
    auditee_fiscal_period_start = forms.CharField(required=False)
    audit_period_covered = forms.CharField(required=False)
    audit_period_other_months = forms.CharField(required=False)
    ein = forms.CharField(
        required=False,
        validators=[ein_validator]  # validators are not run against empty fields
    )
    ein_not_an_ssn_attestation = forms.BooleanField(required=False)
    multiple_eins_covered = forms.BooleanField(required=False)
    auditee_uei = forms.CharField(required=False)
    multiple_ueis_covered = forms.BooleanField(required=False)
    auditee_name = forms.CharField(required=False)
    auditee_address_line_1 = forms.CharField(required=False)
    auditee_city = forms.CharField(
        required=False,
        validators=[alpha_validator]  # validators are not run against empty fields
    )
    auditee_state = forms.CharField(required=False)
    auditee_zip = forms.CharField(required=False)
    auditee_contact_name = forms.CharField(required=False)
    auditee_contact_title = forms.CharField(required=False)
    auditee_phone = forms.CharField(required=False)
    auditee_email = forms.CharField(required=False)
    auditor_firm_name = forms.CharField(required=False)
    auditor_ein = forms.CharField(
        required=False,
        validators=[ein_validator]  # validators are not run against empty fields
    )
    auditor_ein_not_an_ssn_attestation = forms.BooleanField(required=False)
    auditor_country = forms.CharField(required=False)
    auditor_address_line_1 = forms.CharField(required=False)
    auditor_city = forms.CharField(
        required=False,
        validators=[alpha_validator]  # validators are not run against empty fields
    )
    auditor_state = forms.CharField(required=False)
    auditor_zip = forms.CharField(required=False)
    auditor_contact_name = forms.CharField(required=False)
    auditor_contact_title = forms.CharField(required=False)
    auditor_phone = forms.CharField(required=False)
    auditor_email = forms.CharField(required=False)
    secondary_auditors_exist = forms.BooleanField(required=False)
