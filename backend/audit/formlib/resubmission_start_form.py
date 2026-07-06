from django import forms
from django.core.exceptions import ValidationError

from audit.check_resubmission_allowed import check_resubmission_allowed
from audit.models.constants import STATUS, RESUBMISSION_ACTION
from audit.models import SingleAuditChecklist

MATERIAL_CHANGE_CHOICES = [
    ("auditor_report", "Auditor's Report Corrections or Additions"),
    (
        "awards",
        "Awards Corrections or Additions (such as ALN, federal program name, cluster name, etc.)",
    ),
    ("corrective_action_plans", "Corrective Action Plan Corrections or Additions"),
    ("direct_passthrough", "Direct vs. Pass-through Funding Corrections"),
    ("financial_statements", "Financial Statements Corrections or Additions"),
    (
        "findings",
        "Findings Corrections or Additions (such as condition, criteria, cause, effect, "
        "material weakness, significant deficiency, etc.)",
    ),
    ("internal_control", "Internal Control and Compliance Corrections or Additions"),
    ("major_program", "Major Program Determination Corrections"),
    (
        "auditor_professional_requirements",
        "Previous Audit Performed by an Auditor Not Meeting Professional Requirements",
    ),
    ("prior_findings", "Prior Findings Corrections or Additions"),
    ("questioned_costs", "Questioned Costs Corrections or Additions"),
    ("risk", "Risk Determination Correction"),
    ("incomplete_audit_package", "Single Audit Package Completion"),
    ("sefa_award_amounts", "SEFA Reporting Corrections or Additions"),
    ("sf_sac", "SF-SAC Materially Incomplete or Inconsistent with Audit Report"),
]

NON_MATERIAL_CHANGE_CHOICES = [
    ("aln_where_sefa_accurate", "Assistance Listing Numbers (ALNs) Corrections Where SEFA is Accurate"),
    ("data_entry", "Data Entry Corrections not Affecting Audit Conclusions"),
    ("direct_passthrough_where_sefa_accurate", "Direct vs. Pass-through Funding Corrections Where SEFA is Accurate"),
    ("ein", "Employer Identification Number (EIN) Corrections or Additions"),
    ("presentation", "Labelling or Presentation Corrections Not Impacting Reporting, Compliance, or Audit Conclusions"),
    ("rounding", "Minor Numerical Rounding Corrections with No Material Affect on Expenditures, Major Program Determinations, Findings, or Compliance"),
    ("spelling", "Spelling and Typographical Corrections"),
    ("questioned_costs_where_report_accurate", "Questioned Costs Corrections Where Audit Report and Findings are Accurate"),
]

RESUBMISSION_ACTION_CHOICES = [
    (
        RESUBMISSION_ACTION.AUDIT_PDF,
        "I need to upload or edit the audit PDF package (with the option to also edit the SF-SAC data collection forms). I understand that this option will result in a new acceptance date for the submission.",
    ),
    (
        RESUBMISSION_ACTION.SFSAC_ONLY,
        "I only need to modify SF-SAC Data Collection Form information. I understand that the submission's acceptance date will not change.",
    ),
]

RESUBMISSION_REQUESTER_CHOICES = [
    ("auditee", "The Auditee is requesting this resubmission."),
    ("auditor", "The Auditor is requesting this resubmission."),
    ("oversight_official", "An Oversight Official is requesting this resubmission."),
]


class ResubmissionActionForm(forms.Form):
    resubmission_action = forms.ChoiceField(
        choices=RESUBMISSION_ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "usa-radio__input"}),
        required=True,
        error_messages={
            "required": "Select the type of change you need to make.",
        },
    )

    resubmission_requester = forms.MultipleChoiceField(
        required=False,
        choices=RESUBMISSION_REQUESTER_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "usa-checkbox__input"}),
    )

    material_change_reasons = forms.MultipleChoiceField(
        required=False,
        choices=MATERIAL_CHANGE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "usa-checkbox__input"}),
    )

    non_material_change_reasons = forms.MultipleChoiceField(
        required=False,
        choices=NON_MATERIAL_CHANGE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "usa-checkbox__input"}),
    )

    def clean(self):
        cleaned_data = super().clean()

        action = cleaned_data.get("resubmission_action")
        requester = cleaned_data.get("resubmission_requester")
        material = cleaned_data.get("material_change_reasons")
        non_material = cleaned_data.get("non_material_change_reasons")

        if not requester:
            self.add_error(
                "resubmission_requester",
                "Select at least one requester.",
            )

        if action == RESUBMISSION_ACTION.AUDIT_PDF and not material:
            self.add_error(
                "material_change_reasons",
                "Select at least one material change.",
            )

        if action == RESUBMISSION_ACTION.SFSAC_ONLY and not non_material:
            self.add_error(
                "non_material_change_reasons",
                "Select at least one non-material change.",
            )

        return cleaned_data


class ResubmissionStartForm(forms.Form):
    material_change_reasons = forms.MultipleChoiceField(
        required=False,
        choices=MATERIAL_CHANGE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "usa-checkbox__input"}),
    )

    non_material_change_reasons = forms.MultipleChoiceField(
        required=False,
        choices=NON_MATERIAL_CHANGE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "usa-checkbox__input"}),
    )
    
    resubmission_requester = forms.MultipleChoiceField(
        required=False,
        choices=RESUBMISSION_REQUESTER_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "usa-checkbox__input"}),
    )

    report_id = forms.CharField(required=True)

    resubmission_action = forms.ChoiceField(
        choices=RESUBMISSION_ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "usa-radio__input"}),
        required=True,
        error_messages={
            "required": "Select the type of change you need to make.",
        },
    )

    def clean_report_id(self):
        text_input = self.cleaned_data["report_id"]
        report_id = "".join(text_input.split())

        if len(report_id) > 25:
            raise ValidationError("The given report ID is too long!")
        elif len(report_id) < 25:
            raise ValidationError("The given report ID is too short!")

        sac = _validate_report_id_for_resubmission(report_id)
        self.cleaned_data["previous_report_data"] = _gather_previous_report_data(sac)
        self.cleaned_data["resubmission_meta"] = _gather_resubmission_metadata(sac)

        return report_id

    def clean(self):
        cleaned_data = super().clean()

        action = cleaned_data.get("resubmission_action")
        requester = cleaned_data.get("resubmission_requester")
        material = cleaned_data.get("material_change_reasons")
        non_material = cleaned_data.get("non_material_change_reasons")

        if action and not requester:
            self.add_error(
                "resubmission_requester",
                "Select at least one requester.",
            )

        if action == RESUBMISSION_ACTION.AUDIT_PDF and not material:
            self.add_error(
                "material_change_reasons",
                "Select at least one material change.",
            )

        if action == RESUBMISSION_ACTION.SFSAC_ONLY and not non_material:
            self.add_error(
                "non_material_change_reasons",
                "Select at least one non-material change.",
            )

        return cleaned_data


def _validate_report_id_for_resubmission(report_id):
    """
    Given a report_id, determine if it points at a SAC that is eligible for resubmission.
    If not, raise a `ValidatonError` with a helpful message.

    When run by an overridden `clean_{fieldname}` function, `ValidationError`s will be captured and
    added to the form, to be presented to the user.
    """
    # See if a previous submission matches with the given report_id.
    try:
        sac = SingleAuditChecklist.objects.get(
            report_id=report_id,
            submission_status__in=[STATUS.DISSEMINATED, STATUS.RESUBMITTED],
        )
    except SingleAuditChecklist.DoesNotExist:
        raise ValidationError("Audit to resubmit not found.")

    # Further validate the previous submission.
    allowed, reason = check_resubmission_allowed(sac)
    if not allowed:
        raise ValidationError(reason)

    return sac


def _gather_previous_report_data(sac):
    """
    Given a sac, return an object containing the UEI and fiscal period.
    """
    return {
        "auditee_uei": getattr(sac, "auditee_uei").upper(),
        "auditee_name": getattr(sac, "auditee_name"),
        "auditee_fiscal_period_start": getattr(sac, "auditee_fiscal_period_start"),
        "auditee_fiscal_period_end": getattr(sac, "auditee_fiscal_period_end"),
    }


def _gather_resubmission_metadata(sac):
    """
    Given a sac, return an object containing its row_id, report_id, and the next version number.

    If the SAC has resubmission_meta with a version, bump it by one. If not, assume the next version number is 2.
    """
    if getattr(sac, "resubmission_meta"):
        version = sac.resubmission_meta["version"] + 1
    else:
        version = 2

    return {
        "previous_row_id": sac.id,
        "previous_report_id": sac.report_id,
        "version": version,
    }
