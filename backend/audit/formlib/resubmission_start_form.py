from django import forms
from django.core.exceptions import ValidationError

from audit.models import SingleAuditChecklist
from audit.check_resubmission_allowed import check_resubmission_allowed


class ResubmissionStartForm(forms.Form):
    report_id = forms.CharField(required=True)

    def clean_report_id(self):
        """
        Validates the report_id text that comes in from the user.

        Ensures the report_id points to an exiwsting record that is eligible for resubmission.
        """
        text_input = self.cleaned_data["report_id"]

        # 1. Remove all whitespace
        text_input = "".join(text_input.split())

        # 2. Field validations
        if len(text_input) > 25:
            raise ValidationError("The given report ID is too long!")
        elif len(text_input) < 25:
            raise ValidationError("The given report ID is too short!")

        # 3. Try to find the specified report and add the row ID to the form data.
        try:
            sac = SingleAuditChecklist.objects.get(
                report_id=text_input, submission_status="disseminated"
            )
        except SingleAuditChecklist.DoesNotExist:
            raise ValidationError("Audit to resubmit not found.")

        # 4. Check if resubmission is allowed
        allowed, reason = check_resubmission_allowed(sac)
        if not allowed:
            raise ValidationError(reason)

        # Store sac data for use in the view
        self.cleaned_data["previous_report_data"] = _gather_previous_report_data(sac)
        self.cleaned_data["resubmission_meta"] = _gather_resubmission_metadata(sac)

        # The field is clean, return it by default.
        return text_input


def _gather_previous_report_data(sac):
    """
    Given a sac, return an object containing the UEI and fiscal period.
    """
    return {
        "auditee_uei": getattr(sac, "auditee_uei"),
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
