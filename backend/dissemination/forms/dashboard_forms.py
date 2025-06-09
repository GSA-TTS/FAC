from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from config.settings import STATE_ABBREVS

class AnalyticsFilterForm(forms.Form):
    # Multiple choice field Tuples. "choices" variable in field declaration.
    AY_choices = tuple(
        (x, str(x)) for x in reversed(range(2016, date.today().year + 1))
    )  # (2016, "2016"), ..., (current_year, "current_year"))

    # Fields
    audit_year = forms.MultipleChoiceField(
        choices=AY_choices, initial=[2023], required=False
    )
    auditee_state = forms.CharField(required=True)

    # These cleaning functions will run when `form.is_valid()` is run
    def clean_auditee_state(self):
        """
        If the auditee_state is present and is not a valid state (one of STATE_ABBREVS), provide an error.
        """
        auditee_state = self.cleaned_data["auditee_state"]
        if not auditee_state:
            return auditee_state

        if auditee_state not in STATE_ABBREVS:
            raise ValidationError(
                f'"{auditee_state}" is not a valid state abbreviation.'
            )
        return auditee_state

    # Only necessary if the trend_analytics includes an "All years" option.
    # def clean_audit_year(self):
    #     """
    #     If "All years" is selected, don't include any years.
    #     """
    #     audit_year = self.cleaned_data["audit_year"]
    #     if "all_years" in audit_year:
    #         return []
    #     return audit_year
