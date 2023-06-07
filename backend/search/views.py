from django.shortcuts import render, redirect
from django.core.exceptions import BadRequest
from django.views import generic
from django.http.request import HttpRequest

from .forms import SearchForm

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
                        search_query = "vw_federal_award?audit_year=eq.{}".format(query)
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
            SEARCH_URL = (
                "https://api.data.gov/TEST/audit-clearinghouse/v0/dissemination/"
            )
            API_KEY = os.getenv("API_GOV_KEY")
            params = request.GET.dict()
            params["api_key"] = API_KEY
            # Artificial hard limit, to avoid too-long requests or potential API crashes
            if params.get("limit", None) == None or int(params["limit"]) > 1000:
                params["limit"] = "1000"

            initial_response = requests.get(SEARCH_URL + search_path, params=params)
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
                cross_search_path = "vw_auditee"
                cross_search_params = {"limit": 100, "api_key": API_KEY}
                cross_id_list = []
                for x in initial_results:
                    if x.get("auditee_id"):
                        cross_id_list.append(x["auditee_id"])
                temp = "in.("
                for y in cross_id_list:
                    temp += str(y) + ","
                temp = temp[:-1]
                temp += ")"
                cross_search_params["id"] = str(temp)
                cross_results = requests.get(
                    SEARCH_URL + cross_search_path, params=cross_search_params
                )
                for x in initial_results:
                    for y in json.loads(cross_results.text):
                        if x.get("auditee_id") == y.get("id"):
                            x["uei_list"] = y.get("uei_list")
                            x["auditee_city"] = y.get("auditee_city")
                            x["auditee_state"] = y.get("auditee_state")
                            x["duns_list"] = y.get("duns_list")

            # Cross vw_federal_award.cpa_ein with vw_auditee.ein_list[0]
            elif search_path == "vw_federal_award":
                cross_search_path = "vw_auditee"
                cross_search_params = {"limit": 100, "api_key": API_KEY}
                cross_id_list = []
                for x in initial_results:
                    if x.get("cpa_ein"):
                        cross_id_list.append(x["cpa_ein"])
                temp = "cd.{"
                for y in cross_id_list:
                    temp += str(y) + ","
                temp = temp[:-1]
                temp += "}"
                cross_search_params["ein_list"] = str(temp)
                cross_response = requests.get(
                    SEARCH_URL + cross_search_path, params=cross_search_params
                )
                cross_results = json.loads(cross_response.text)
                for x in initial_results:
                    for y in cross_results:
                        if x.get("cpa_ein") == y.get("ein_list")[0]:
                            x["uei_list"] = y.get("uei_list")
                            x["auditee_name"] = y.get("auditee_name")
                            x["auditee_city"] = y.get("auditee_city")
                            x["auditee_state"] = y.get("auditee_state")
                            x["duns_list"] = y.get("duns_list")

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
