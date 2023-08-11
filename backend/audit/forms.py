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
    # These should probably have the lowercase values from Jsonnet:
    choices_GAAP = (
        ("unmodified_opinion", "Unmodified opinion"),
        ("qualified_opinion", "Qualified opinion"),
        ("adverse_opinion", "Adverse opinion"),
        ("disclaimer_of_opinion", "Disclaimer of opinion"),
        (
            "not_gaap",
            "Financial statements were not prepared in accordance with GAAP but were prepared in accordance with a special purpose framework.",
        ),
    )
    choices_SP_FRAMEWORK_BASIS = (
        (
            "cash_basis",
            "Cash basis",
        ),
        (
            "tax_basis",
            "Tax basis",
        ),
        (
            "contractual_basis",
            "Contractual basis",
        ),
        (
            "other_basis",
            "Other basis",
        ),
    )
    choices_SP_FRAMEWORK_OPINIONS = (
        (
            "unmodified_opinion",
            "Unmodified opinion",
        ),
        (
            "qualified_opinion",
            "Qualified opinion",
        ),
        (
            "adverse_opinion",
            "Adverse opinion",
        ),
        (
            "disclaimer_of_opinion",
            "Disclaimer of opinion",
        ),
    )

    choices_agencies = list((i, i) for i in AGENCY_NAMES)

    gaap_results = forms.MultipleChoiceField(choices=choices_GAAP)
    sp_framework_basis = forms.MultipleChoiceField(choices=choices_SP_FRAMEWORK_BASIS)
    is_sp_framework_required = forms.MultipleChoiceField(choices=choices_YoN)
    sp_framework_opinions = forms.MultipleChoiceField(
        choices=choices_SP_FRAMEWORK_OPINIONS
    )
    is_going_concern_included = forms.MultipleChoiceField(choices=choices_YoN)
    is_internal_control_deficiency_disclosed = forms.MultipleChoiceField(
        choices=choices_YoN
    )
    is_internal_control_material_weakness_disclosed = forms.MultipleChoiceField(
        choices=choices_YoN
    )
    is_material_noncompliance_disclosed = forms.MultipleChoiceField(choices=choices_YoN)
    is_aicpa_audit_guide_included = forms.MultipleChoiceField(choices=choices_YoN)
    dollar_threshold = forms.IntegerField(min_value=1)
    is_low_risk_auditee = forms.MultipleChoiceField(choices=choices_YoN)
    agencies = forms.MultipleChoiceField(choices=choices_agencies)
