from django.shortcuts import render, redirect
from django.core.exceptions import BadRequest
from django.views import generic

from .forms import SearchForm
from .utils import cross_reference_federal_award, cross_reference_general

import os
import json
import requests


class SearchHome(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            context = {"test": "sample text"}

            return render(request, "search/search-page.html", context)
        except Exception as e:
            raise BadRequest(e)

    def post(self, request, *args, **kwargs):
        try:
            form = SearchForm(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                search_by = form.cleaned_data["search_by"]
                search_query = ""

                match search_by:
                    case "UEI":
                        search_query = "vw_auditee?uei_list=cd.{{ {} }}".format(query)
                    case "EIN":
                        search_query = "vw_auditee?ein_list=cd.{{ {} }}".format(query)
                    case "FY":
                        search_query = "vw_general?audit_year=eq.{}".format(query)
                    case "ALN":
                        search_query = "vw_federal_award?agency_cfda=eq.{}".format(
                            query
                        )
                    case _:
                        raise BadRequest()

                search_query += "&limit=100"
                return redirect(str(request.build_absolute_uri() + search_query))
            else:
                return render(request, "search/search-page.html")

        except Exception as e:
            raise BadRequest(e)


class SearchResults(generic.View):
    # If no search was made, load the homepage.
    # Otherwise, process parameters, make request to API, and display results
    def get(self, request, *args, **kwargs):
        search_path = kwargs.get("search_path", "")
        try:
            SEARCH_URL = os.getenv("API_GOV_URL")
            API_KEY = os.getenv("API_GOV_KEY")
            params = request.GET.dict()
            params["api_key"] = API_KEY
            # Artificial hard limit, to avoid too-long requests or potential API crashes
            if params.get("limit") is None or int(params["limit"]) > 1000:
                params["limit"] = "1000"

            initial_response = requests.get(
                SEARCH_URL + search_path, params=params, timeout=10
            )
            initial_results = json.loads(initial_response.text)
            context = {
                "search_path": search_path,
                "search_params": request.GET.dict(),
                "search_status_code": initial_response.status_code,
                "disclaimer_accepted": request.session.get(
                    "disclaimer_accepted", False
                ),
            }
            if initial_response.status_code != 200:
                return render(request, "search/search-results.html", context)

            # Cross vw_general.auditee_id with vw_auditee.id
            if search_path == "vw_general":
                initial_results = cross_reference_general(initial_results)

            # Cross vw_federal_award.cpa_ein with vw_auditee.ein_list[0]
            elif search_path == "vw_federal_award":
                initial_results = cross_reference_federal_award(initial_results)

            context["results"] = initial_results

            return render(request, "search/search-results.html", context)
        except Exception as e:
            raise BadRequest(e)

    # When user accepts the disclaimer, save in session and reload the page
    def post(self, request, *args, **kwargs):
        try:
            request.session["disclaimer_accepted"] = True

            return redirect(request.build_absolute_uri())
        except Exception as e:
            raise BadRequest(e)
