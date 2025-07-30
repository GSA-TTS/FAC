from django import forms
from django.core.exceptions import ValidationError

from audit.models import SingleAuditChecklist


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
            self.cleaned_data["sac_row_id"] = sac.id
            # If the previous SAC had a version, bump by one and pass it back.
            # If not, we assume this is version 2 for now.
            if getattr(sac, "resubmission_meta"):
                self.cleaned_data["version"] = sac.resubmission_meta["version"] + 1
            else:
                self.cleaned_data["version"] = 2
        except SingleAuditChecklist.DoesNotExist:
            raise ValidationError("Audit to resubmit not found.")

        # The field is clean, return it.
        return text_input
