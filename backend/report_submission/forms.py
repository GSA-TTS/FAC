from django import forms

# The general information fields are currently specified in two places:
#   - report_submission.forms.GeneralInformationForm
#   - schemas.sections.GeneralInformation.schema.json


class GeneralInformationForm(forms.Form):
    audit_type = forms.CharField()
    auditee_fiscal_period_end = forms.CharField()
    auditee_fiscal_period_start = forms.CharField()
    audit_period_covered = forms.CharField()
    ein = forms.CharField()
    ein_not_an_ssn_attestation = forms.BooleanField(required=False)
    multiple_eins_covered = forms.BooleanField(required=False)
    auditee_uei = forms.CharField()
    multiple_ueis_covered = forms.BooleanField(required=False)
    auditee_name = forms.CharField()
    auditee_address_line_1 = forms.CharField()
    auditee_city = forms.CharField()
    auditee_state = forms.CharField()
    auditee_zip = forms.CharField()
    auditee_contact_name = forms.CharField()
    auditee_contact_title = forms.CharField()
    auditee_phone = forms.CharField()
    auditee_email = forms.CharField()
    auditor_firm_name = forms.CharField()
    auditor_ein = forms.CharField()
    auditor_ein_not_an_ssn_attestation = forms.BooleanField(required=False)
    auditor_country = forms.CharField()
    auditor_address_line_1 = forms.CharField()
    auditor_city = forms.CharField()
    auditor_state = forms.CharField()
    auditor_zip = forms.CharField()
    auditor_contact_name = forms.CharField()
    auditor_contact_title = forms.CharField()
    auditor_phone = forms.CharField()
    auditor_email = forms.CharField()


class UploadReportForm(forms.Form):
    financial_statements = forms.IntegerField(min_value=1)
    financial_statements_opinion = forms.IntegerField(min_value=1)
    schedule_expenditures = forms.IntegerField(min_value=1)
    schedule_expenditures_opinion = forms.IntegerField(
        min_value=1
    )
    uniform_guidance_control = forms.IntegerField(min_value=1)
    uniform_guidance_compliance = forms.IntegerField(min_value=1)
    GAS_control = forms.IntegerField(min_value=1)
    GAS_compliance = forms.IntegerField(min_value=1)
    schedule_findings = forms.IntegerField(min_value=1)
    schedule_prior_findings = forms.IntegerField(
        initial=0, required=False, min_value=1
    )
    CAP_page = forms.IntegerField(
        initial=0, required=False, min_value=1
    )
    upload_report = forms.FileField()
