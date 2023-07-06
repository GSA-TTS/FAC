from django import forms

class UploadReportForm(forms.Form):
    financial_statements = forms.IntegerField(min_value=1)
    financial_statements_opinion = forms.IntegerField(min_value=1)
    schedule_expenditures = forms.IntegerField(min_value=1)
    schedule_expenditures_opinion = forms.IntegerField(min_value=1)
    uniform_guidance_control = forms.IntegerField(min_value=1)
    uniform_guidance_compliance = forms.IntegerField(min_value=1)
    GAS_control = forms.IntegerField(min_value=1)
    GAS_compliance = forms.IntegerField(min_value=1)
    schedule_findings = forms.IntegerField(min_value=1)
    schedule_prior_findings = forms.IntegerField(initial=0, required=False, min_value=1)
    CAP_page = forms.IntegerField(initial=0, required=False, min_value=1)
    upload_report = forms.FileField()
