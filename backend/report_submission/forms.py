from django import forms
from django.core.validators import RegexValidator
from config.settings import CHARACTER_LIMITS_GENERAL, STATE_ABBREVS

from api.uei import get_uei_info_from_sam_gov


# Regex for words, includes non-[A-Z] ASCII characters like ñ and ī.
# \A and \Z start and terminate the string.
# [^\W\d] - matches values _not_ in W (non-word characters) or d (digits), which is all alphas, including diacritics.
# [^\W\d] is OR'd with \s to allow whitespace instead of another character, to allow spaces.
# [^\W\d]|\s is wrapped in parenthesis and appended by a plus to allow any number of characters.
alpha_validator = RegexValidator(
    r"\A([^\W\d]|\s)+\Z", "This field should not include numbers or special characters."
)
date_validator = RegexValidator(
    r"^([0-9]{2}/[0-9]{2}/[0-9]{4})|([0-9]{4}-[0-9]{2}-[0-9]{4})$",
    "Dates should be in the format MM/DD/YYYY",
)
ein_validator = RegexValidator(
    r"^[0-9]{9}$", "EINs should be nine characters long and be made up of only numbers."
)
phone_validator = RegexValidator(
    r"^[1-9]{1}[0-9]{9}$",
    "Phone numbers should be ten numbers long, cannot include spaces or symbols such as '-' or '+', and cannot begin with a zero.",
)
zip_validator = RegexValidator(
    r"^[0-9]{5}(?:[0-9]{4})?$", "Zip codes should be in the format 12345 or 12345-1234."
)


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
    max_string_length = 100
    foreign_address_max_length = 500
    choices_state_abbrevs = list((i, i) for i in STATE_ABBREVS)

    audit_type = forms.CharField(required=False)
    auditee_fiscal_period_end = forms.CharField(
        required=False, validators=[date_validator]
    )
    auditee_fiscal_period_start = forms.CharField(
        required=False, validators=[date_validator]
    )
    audit_period_covered = forms.CharField(required=False)
    audit_period_other_months = forms.CharField(
        required=False,
        min_length=CHARACTER_LIMITS_GENERAL["number_months"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["number_months"]["max"],
    )
    ein = forms.CharField(
        required=False,
        validators=[ein_validator],  # validators are not run against empty fields
    )
    ein_not_an_ssn_attestation = forms.BooleanField(required=False)
    multiple_eins_covered = forms.BooleanField(required=False)
    auditee_uei = forms.CharField(required=False)
    multiple_ueis_covered = forms.BooleanField(required=False)
    auditee_name = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditee_name"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditee_name"]["max"],
        required=False,
    )
    auditee_address_line_1 = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditee_address_line_1"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditee_address_line_1"]["max"],
        required=False,
    )
    auditee_city = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditee_city"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditee_city"]["max"],
        required=False,
        validators=[alpha_validator],  # validators are not run against empty fields
    )
    auditee_state = forms.ChoiceField(choices=choices_state_abbrevs, required=False)
    auditee_zip = forms.CharField(required=False, validators=[zip_validator])
    auditee_contact_name = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditee_contact_name"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditee_contact_name"]["max"],
        required=False,
    )
    auditee_contact_title = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditee_contact_title"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditee_contact_title"]["max"],
        required=False,
    )
    auditee_phone = forms.CharField(required=False, validators=[phone_validator])
    auditee_email = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditee_email"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditee_email"]["max"],
        required=False,
    )
    auditor_firm_name = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditor_firm_name"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditor_firm_name"]["max"],
        required=False,
    )
    auditor_ein = forms.CharField(
        required=False,
        validators=[ein_validator],  # validators are not run against empty fields
    )
    auditor_ein_not_an_ssn_attestation = forms.BooleanField(required=False)
    auditor_country = forms.CharField(required=False)
    auditor_international_address = forms.CharField(
        max_length=foreign_address_max_length, required=False
    )
    auditor_address_line_1 = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditor_address_line_1"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditor_address_line_1"]["max"],
        required=False,
    )
    auditor_city = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditor_city"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditor_city"]["max"],
        required=False,
        validators=[alpha_validator],  # validators are not run against empty fields
    )
    auditor_state = forms.ChoiceField(choices=choices_state_abbrevs, required=False)
    auditor_zip = forms.CharField(required=False, validators=[zip_validator])
    auditor_contact_name = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditor_contact_name"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditor_contact_name"]["max"],
        required=False,
    )
    auditor_contact_title = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditor_contact_title"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditor_contact_title"]["max"],
        required=False,
    )
    auditor_phone = forms.CharField(required=False, validators=[phone_validator])
    auditor_email = forms.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditor_email"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditor_email"]["max"],
        required=False,
    )
    secondary_auditors_exist = forms.BooleanField(required=False)
