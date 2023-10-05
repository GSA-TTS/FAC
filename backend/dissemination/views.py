from django import forms
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from hashlib import sha1
import json
import random

search_db = {}
results_db = {}


class SearchForm(forms.Form):
    value = forms.CharField(label="Value")


def execute_search(search_id):
    search_key = search_db[search_id]

    # we won't actually save search results, just doing this for demo purposes
    if search_id in results_db.keys():
        result = results_db[search_id]
    else:
        result = [
            {"value": random.randrange(0, 100)},
            {"value": random.randrange(0, 100)},
            {"value": random.randrange(0, 100)},
        ]

        results_db[search_id] = result

    return search_key, search_id, result


def gen_search_id(form):
    search_key = json.dumps(form.cleaned_data)
    search_id = sha1(search_key.encode("utf-8")).hexdigest()
    search_db[search_id] = search_key
    return search_key, search_id


class Search(View):
    def get(self, request, *args, **kwargs):
        form = SearchForm()

        return render(request, "search.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)

        if form.is_valid():
            _, search_id = gen_search_id(form)

            return redirect(reverse("dissemination:SavedSearch", args=[search_id]))


class SavedSearch(View):
    def get(self, request, search_id):
        search_key, search_id, results = execute_search(search_id)

        search_params = json.loads(search_key)

        form = SearchForm(search_params)

        return render(request, "search.html", {"form": form, "results": results})
