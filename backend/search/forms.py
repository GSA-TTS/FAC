from django import forms


class SearchForm(forms.Form):
    fiscal_year_choices = ((2022, 2022),)

    UEI_EIN = forms.CharField(required=False, label="UEI_EIN", max_length=1024)
    ALN = forms.CharField(required=False, label="ALN", max_length=1024)
    fiscal_year = forms.MultipleChoiceField(
        required=False, label="fiscal_year", choices=fiscal_year_choices
    )
    acceptance_start_date = forms.DateField(
        required=False, label="acceptance_start_date_input"
    )
    acceptance_end_date = forms.DateField(
        required=False, label="acceptance_end_date_input"
    )
