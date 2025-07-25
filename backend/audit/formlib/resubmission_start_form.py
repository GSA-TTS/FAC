from django import forms
from django.core.exceptions import ValidationError

from audit.models import SingleAuditChecklist
from audit.check_resubmission_allowed import check_resubmission_allowed


class ResubmissionStartForm(forms.Form):
    report_id = forms.CharField(required=True)

    def clean_report_id(self):
        """
        Validates the report_id text that comes in from the user.
        """
        text_input = self.cleaned_data["report_id"]

        # 1. Remove all whitespace
        text_input = "".join(text_input.split())

        # 2. Field validations. Maybe regex? If it's not going to end up in eighty places.
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

        # Store sac ID for use in the view
        self.cleaned_data["sac_row_id"] = sac.id

        # The field is clean, return it.
        return text_input
