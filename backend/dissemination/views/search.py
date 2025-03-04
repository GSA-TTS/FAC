import logging
import math

import time
from datetime import date

from config.settings import STATE_ABBREVS, SUMMARY_REPORT_DOWNLOAD_LIMIT
from dissemination.forms import AdvancedSearchForm, SearchForm

from dissemination.search import gather_errors
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from dissemination.searchlib.search_utils import (
    populate_cog_over_name,
    run_search,
    audit_populate_cog_over_name,
)
from dissemination.views.utils import include_private_results
from support.decorators import newrelic_timing_metric

logger = logging.getLogger(__name__)

default_checked_audit_years = [
    date.today().year,
    date.today().year - 1,
]  # Auto-check this and last year


# TODO: Update Post SOC Launch -> Delete Advanced/Search, have 1 search.
class AdvancedSearch(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AdvancedSearch, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        When accessing the search page through get, return the blank search page.
        """
        form = AdvancedSearchForm()

        return render(
            request,
            "search.html",
            {
                "advanced_search_flag": True,
                "form": form,
                "form_user_input": {"audit_year": default_checked_audit_years},
                "state_abbrevs": STATE_ABBREVS,
                "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
            },
        )

    @newrelic_timing_metric("search-advanced")
    def post(self, request, *args, **kwargs):
        """
        When accessing the search page through post, run a search and display the results.
        """
        time_starting_post = time.time()

        form = AdvancedSearchForm(request.POST)
        paginator_results = None
        results_count = None
        page = 1
        results = []
        errors = []
        context = {}

        # Obtain cleaned form data.
        form.is_valid()
        form_data = form.cleaned_data
        form_user_input = {k: v[0] if len(v) == 1 else v for k, v in form.data.lists()}

        # build error list.
        errors = gather_errors(form)

        # Tells the backend we're running advanced search.
        form_data["advanced_search_flag"] = True

        logger.info(f"Advanced searching on fields: {form_data}")

        include_private = include_private_results(request)

        # Generate results on valid user input.
        if form.is_valid():
            results = run_search(form_data)

            results_count = results.count()

            # Reset page to one if the page number surpasses how many pages there actually are
            page = form_data["page"]
            ceiling = math.ceil(results_count / form_data["limit"])
            if not page or page > ceiling or page < 1:
                page = 1

            logger.info(f"TOTAL: results_count: [{results_count}]")

            # The paginator object handles splicing the results to a one-page iterable and calculates which page numbers to show.
            paginator = Paginator(object_list=results, per_page=form_data["limit"])
            paginator_results = paginator.get_page(page)
            paginator_results.adjusted_elided_pages = paginator.get_elided_page_range(
                page, on_each_side=1
            )

        # Reformat dates for pre-populating the USWDS date-picker.
        if form_data.get("start_date"):
            form_user_input["start_date"] = form_data["start_date"].strftime("%Y-%m-%d")
        if form_data.get("end_date"):
            form_user_input["end_date"] = form_data["end_date"].strftime("%Y-%m-%d")

        # populate the agency name in cog/over field
        paginator_results = populate_cog_over_name(paginator_results)

        context = context | {
            "advanced_search_flag": True,
            "form_user_input": form_user_input,
            "form": form,
            "errors": errors,
            "include_private": include_private,
            "limit": form_data["limit"],
            "order_by": form_data["order_by"],
            "order_direction": form_data["order_direction"],
            "page": page,
            "results_count": results_count,
            "results": paginator_results,
            "state_abbrevs": STATE_ABBREVS,
            "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
        }
        time_beginning_render = time.time()
        total_time_ms = int(
            math.ceil((time_beginning_render - time_starting_post) * 1000)
        )
        total_time_s = total_time_ms / 1000
        logger.info(f"Total time between post and render {total_time_ms}ms")
        return render(request, "search.html", context | {"total_time_s": total_time_s})


class Search(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(Search, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        When accessing the search page through get, return the blank search page.
        """
        form = SearchForm()

        return render(
            request,
            "search.html",
            {
                "advanced_search_flag": False,
                "form": form,
                "form_user_input": {"audit_year": default_checked_audit_years},
                "state_abbrevs": STATE_ABBREVS,
                "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
            },
        )

    @newrelic_timing_metric("search")
    def post(self, request, *args, **kwargs):
        """
        When accessing the search page through post, run a search and display the results.
        """
        time_starting_post = time.time()

        form = SearchForm(request.POST)
        paginator_results = None
        results_count = None
        page = 1
        results = []
        errors = []
        context = {}

        # Obtain cleaned form data.
        form.is_valid()
        form_data = form.cleaned_data
        form_user_input = {k: v[0] if len(v) == 1 else v for k, v in form.data.lists()}

        # build error list.
        errors = gather_errors(form)

        # Tells the backend we're running basic search.
        form_data["advanced_search_flag"] = False

        logger.info(f"Searching on fields: {form_data}")

        include_private = include_private_results(request)

        # Generate results on valid user input.
        if form.is_valid():
            results = run_search(form_data)

            results_count = results.count()

            # Reset page to one if the page number surpasses how many pages there actually are
            page = form_data["page"]
            ceiling = math.ceil(results_count / form_data["limit"])
            if not page or page > ceiling or page < 1:
                page = 1

            logger.info(f"TOTAL: results_count: [{results_count}]")

            # The paginator object handles splicing the results to a one-page iterable and calculates which page numbers to show.
            paginator = Paginator(object_list=results, per_page=form_data["limit"])
            paginator_results = paginator.get_page(page)
            paginator_results.adjusted_elided_pages = paginator.get_elided_page_range(
                page, on_each_side=1
            )

        # Reformat dates for pre-populating the USWDS date-picker.
        if form_data.get("start_date"):
            form_user_input["start_date"] = form_data["start_date"].strftime("%Y-%m-%d")
        if form_data.get("end_date"):
            form_user_input["end_date"] = form_data["end_date"].strftime("%Y-%m-%d")

        # populate the agency name in cog/over field
        paginator_results = populate_cog_over_name(paginator_results)

        context = context | {
            "advanced_search_flag": False,
            "form_user_input": form_user_input,
            "form": form,
            "errors": errors,
            "include_private": include_private,
            "limit": form_data["limit"],
            "order_by": form_data["order_by"],
            "order_direction": form_data["order_direction"],
            "page": page,
            "results_count": results_count,
            "results": paginator_results,
            "state_abbrevs": STATE_ABBREVS,
            "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
        }
        time_beginning_render = time.time()
        total_time_ms = int(
            math.ceil((time_beginning_render - time_starting_post) * 1000)
        )
        total_time_s = total_time_ms / 1000
        logger.info(f"Total time between post and render {total_time_ms}ms")
        return render(request, "search.html", context | {"total_time_s": total_time_s})


class AuditSearch(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AuditSearch, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        When accessing the search page through get, return the blank search page.

        Reusing existing AdvancedSearch Form.
        """
        form = AdvancedSearchForm()

        return render(
            request,
            "search_audit.html",
            {
                "form": form,
                "form_user_input": {"audit_year": default_checked_audit_years},
                "state_abbrevs": STATE_ABBREVS,
                "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
            },
        )

    @newrelic_timing_metric("search")
    def post(self, request, *args, **kwargs):
        """
        When accessing the search page through post, run a search and display the results.
        """
        time_starting_post = time.time()

        form = AdvancedSearchForm(request.POST)
        paginator_results = None
        results_count = None
        page = 1
        context = {}

        # Obtain cleaned form data.
        form.is_valid()
        form_data = form.cleaned_data
        form_user_input = {k: v[0] if len(v) == 1 else v for k, v in form.data.lists()}

        # build error list.
        errors = gather_errors(form)

        logger.info(f"Searching on fields: {form_data}")

        include_private = include_private_results(request)

        # Generate results on valid user input.
        if form.is_valid():
            results = run_search(form_data, True)

            results_count = results.count()

            # Reset page to one if the page number surpasses how many pages there actually are
            page = form_data["page"]
            ceiling = math.ceil(results_count / form_data["limit"])
            if not page or page > ceiling or page < 1:
                page = 1

            logger.info(f"TOTAL: results_count: [{results_count}]")

            # The paginator object handles splicing the results to a one-page iterable and calculates which page numbers to show.
            paginator = Paginator(object_list=results, per_page=form_data["limit"])
            paginator_results = paginator.get_page(page)
            paginator_results.adjusted_elided_pages = paginator.get_elided_page_range(
                page, on_each_side=1
            )

        # Reformat dates for pre-populating the USWDS date-picker.
        if form_data.get("start_date"):
            form_user_input["start_date"] = form_data["start_date"].strftime("%Y-%m-%d")
        if form_data.get("end_date"):
            form_user_input["end_date"] = form_data["end_date"].strftime("%Y-%m-%d")

        # populate the agency name in cog/over field
        paginator_results = audit_populate_cog_over_name(paginator_results)

        context = context | {
            "form_user_input": form_user_input,
            "form": form,
            "errors": errors,
            "include_private": include_private,
            "limit": form_data["limit"],
            "order_by": form_data["order_by"],
            "order_direction": form_data["order_direction"],
            "page": page,
            "results_count": results_count,
            "results": paginator_results,
            "state_abbrevs": STATE_ABBREVS,
            "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
        }
        time_beginning_render = time.time()
        total_time_ms = int(
            math.ceil((time_beginning_render - time_starting_post) * 1000)
        )
        total_time_s = total_time_ms / 1000
        logger.info(f"Total time between post and render {total_time_ms}ms")
        return render(request, "search.html", context | {"total_time_s": total_time_s})
