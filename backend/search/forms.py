from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(label="query", max_length=100)
    search_by = forms.CharField(label="search_by", max_length=100)
