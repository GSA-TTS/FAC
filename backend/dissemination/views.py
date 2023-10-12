from django.shortcuts import render
from django.views.generic import View

from dissemination.forms import SearchForm


class Search(View):
    def get(self, request):
        form = SearchForm()
        return render(request, "search.html", {"form": form})

    def post(self, request):
        form = SearchForm(request.POST)

        return render(request, "search.html", {"form": form})
