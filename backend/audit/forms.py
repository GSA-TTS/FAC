from django import forms
from config.settings import AGENCY_NAMES


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


class AuditInfoForm(forms.Form):
    def clean_booleans(self):
        data = self.cleaned_data
        for k, v in data.items():
            if v == ["True"]:
                data[k] = True
            elif v == ["False"]:
                data[k] = False
        self.cleaned_data = data
        return data

    choices_YoN = (("True", "Yes"), ("False", "No"))
    choices_GGAP = (
        ("Unmodified opinion", "Unmodified opinion"),
        ("Qualified opinion", "Qualified opinion"),
        ("Adverse opinion", "Adverse opinion"),
        ("Disclaimer of opinion", "Disclaimer of opinion"),
        (
            "Prepared under non-GGAP framework",
            "Financial statements were not prepared in accordance with GGAP but were prepared in accordance with a special purpose framework.",
        ),
    )
    choices_agencies = list((i, i) for i in AGENCY_NAMES)

    GGAP_results = forms.MultipleChoiceField(choices=choices_GGAP)
    going_concern_included = forms.MultipleChoiceField(choices=choices_YoN)
    internal_control_deficiency_disclosed = forms.MultipleChoiceField(
        choices=choices_YoN
    )
    internal_control_material_weakness_disclosed = forms.MultipleChoiceField(
        choices=choices_YoN
    )
    material_noncompliance_disclosed = forms.MultipleChoiceField(choices=choices_YoN)
    AICPA_audit_guide_included = forms.MultipleChoiceField(choices=choices_YoN)
    dollar_threshold = forms.IntegerField(min_value=1)
    low_risk_auditee = forms.MultipleChoiceField(choices=choices_YoN)
    agencies = forms.MultipleChoiceField(choices=choices_agencies)


class AuditorCertificationStep1Form(forms.Form):
    is_OMB_limited = forms.BooleanField()
    is_auditee_responsible = forms.BooleanField()
    has_used_auditors_report = forms.BooleanField()
    has_no_auditee_procedures = forms.BooleanField()
    is_FAC_releasable = forms.BooleanField()


class AuditorCertificationStep2Form(forms.Form):
    auditor_name = forms.CharField()
    auditor_title = forms.CharField()


class AuditeeCertificationStep1Form(forms.Form):
    has_no_PII = forms.BooleanField()
    has_no_BII = forms.BooleanField()
    meets_2CFR_specifications = forms.BooleanField()
    is_2CFR_compliant = forms.BooleanField()
    is_complete_and_accurate = forms.BooleanField()
    has_engaged_auditor = forms.BooleanField()
    is_issued_and_signed = forms.BooleanField()
    is_FAC_releasable = forms.BooleanField()


class AuditeeCertificationStep2Form(forms.Form):
    auditee_name = forms.CharField()
    auditee_title = forms.CharField()
