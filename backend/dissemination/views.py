from django.shortcuts import render
from django.views.generic import View

from dissemination.forms import SearchForm
from dissemination.search import search_general


class Search(View):
    def get(self, request):
        form = SearchForm()

        return render(request, "search.html", {"form": form})

    def post(self, request):
        form = SearchForm(request.POST)
        results = []

        if form.is_valid():
            names = form.cleaned_data["entity_name"].splitlines()
            uei_or_eins = form.cleaned_data["uei_or_ein"].splitlines()
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            cog_or_oversight = form.cleaned_data["cog_or_oversight"]
            agency_name = form.cleaned_data["agency_name"]

            results = search_general(
                names, uei_or_eins, start_date, end_date, cog_or_oversight, agency_name
            )

        return render(request, "search.html", {"form": form, "results": results})
