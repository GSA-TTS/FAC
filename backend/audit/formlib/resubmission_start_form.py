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

RESUBMISSION_ACTION_CHOICES = [
    (RESUBMISSION_ACTION.AUDIT_PDF, "I need to upload or edit the audit PDF package."),
    (
        RESUBMISSION_ACTION.SFSAC_ONLY,
        "I only need to modify SF-SAC Data Collection Form information.",
    ),
]


class ResubmissionActionForm(forms.Form):
    resubmission_action = forms.ChoiceField(
        choices=RESUBMISSION_ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "usa-radio__input"}),
        required=True,
        initial="audit_pdf",
        error_messages={
            "required": "Select the type of change you need to make.",
        },
    )


class ResubmissionStartForm(forms.Form):
    material_change_reasons = forms.MultipleChoiceField(
        required=True,
        choices=MATERIAL_CHANGE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "usa-checkbox__input"}),
        error_messages={
            "required": "Select at least one reason for resubmission.",
        },
    )

    report_id = forms.CharField(required=True)

    resubmission_action = forms.ChoiceField(
        choices=RESUBMISSION_ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "usa-radio__input"}),
        required=True,
        initial="audit_pdf",
        error_messages={
            "required": "Select the type of change you need to make.",
        },
    )

    def clean_report_id(self):
        """
        Cleans the report_id text that comes in from the user.

        Ensures the report_id points to an existing record that is eligible for resubmission.
        """
        # 1. Remove all whitespace
        text_input = self.cleaned_data["report_id"]
        report_id = "".join(text_input.split())

        # 2. Field validations
        if len(report_id) > 25:
            raise ValidationError("The given report ID is too long!")
        elif len(report_id) < 25:
            raise ValidationError("The given report ID is too short!")

        # 3. Try to find the specified report. Add SAC data to the form data.
        sac = _validate_report_id_for_resubmission(report_id)
        self.cleaned_data["previous_report_data"] = _gather_previous_report_data(sac)
        self.cleaned_data["resubmission_meta"] = _gather_resubmission_metadata(sac)

        # The field is clean, return it by default.
        return report_id


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
