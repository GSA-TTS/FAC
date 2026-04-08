from django import forms
from django.core.exceptions import ValidationError

from audit.check_resubmission_allowed import check_resubmission_allowed
from audit.models.constants import STATUS
from audit.models import SingleAuditChecklist

MATERIAL_CHANGE_CHOICES = [
    ("audit_findings", "Material change to audit findings"),
    ("corrective_action_plans", "Addition or revision of corrective action plans"),
    ("missing_finding_elements", "Inclusion of missing finding elements (such as condition, criteria, cause, or effect)"),
    ("questioned_costs", "Correction to questioned costs or compliance determination"),
    ("major_program_or_low_risk", "Error in major program determination or low-risk auditee status"),
    ("sefa_award_amounts", "Change to federal award amounts in the Schedule of Expenditures of Federal Awards (SEFA)"),
    ("assistance_listing_number", "Correction to Assistance Listing Number"),
    ("incomplete_audit_package", "Supplementing an incomplete Single Audit package (for example, missing financial statements or required reports)"),
    ("auditor_report_elements", "Addition or correction to the required auditor report elements"),
    ("auditor_report_revision", "Revision to the auditor's report"),
]

class ResubmissionStartForm(forms.Form):
    material_change_reasons = forms.MultipleChoiceField(
        required=True,
        choices=MATERIAL_CHANGE_CHOICES,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "usa-checkbox__input"}
        ),
        error_messages={
            "required": "Select at least one reason for resubmission.",
        },
    )
    
    report_id = forms.CharField(required=True)

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
