from django import forms


class SearchForm(forms.Form):
    AY_choices = (
        (x, str(x)) for x in reversed(range(2019, 2024))
    )  # ((2016, "2016"), (2017, "2017"), ..., (2023, "2023"))

    # Query params
    entity_name = forms.CharField(required=False)
    uei_or_ein = forms.CharField(required=False)
    aln = forms.CharField(required=False)
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    cog_or_oversight = forms.CharField(required=False)
    agency_name = forms.CharField(required=False)
    audit_year = forms.MultipleChoiceField(choices=AY_choices, required=False)
    auditee_state = forms.CharField(required=False)

    # Display params
    limit = forms.CharField(required=False)
    page = forms.CharField(required=False)
    order_by = forms.CharField(required=False)
    order_direction = forms.CharField(required=False)
