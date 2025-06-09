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
        choices=AY_choices, initial=[2023], required=True
    )
    auditee_state = forms.CharField(required=False)

    # These cleaning functions will run when `form.is_valid()` is run
    def clean_auditee_state(self):
        """
        If the auditee_state is present and is not a valid state (one of STATE_ABBREVS), provide an error.
        """
        auditee_state = self.cleaned_data.get("auditee_state", "")
        if not auditee_state:
            return auditee_state

        if auditee_state not in STATE_ABBREVS:
            raise ValidationError(
                f'"{auditee_state}" is not a valid state abbreviation.'
            )
        return auditee_state

    def clean_audit_year(self):
        """
        If only one year has been selected, a state must also be chosen.
        """
        audit_year = self.cleaned_data.get("audit_year", [])
        auditee_state = self.cleaned_data.get("auditee_state", "")

        if len(audit_year) == 1 and not auditee_state:
            raise ValidationError(
                "Choose a single year and a state, or choose multiple years."
            )

        return audit_year
