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

    def clean(self):
        """
        'clean' will run after all other fields have been validated.
        Since these fields depend on each other, it is required.
        If only one year has been selected, a state must also be chosen.
        """
        cleaned_data = super().clean()
        audit_years = cleaned_data.get("audit_year", [])
        auditee_state = cleaned_data.get("auditee_state", "")

        if len(audit_years) == 1 and not auditee_state:
            self.add_error(
                "audit_year",
                "Choose a single year and a state, or choose multiple years.",
            )
