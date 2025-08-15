from datetime import date
import logging
import math
import time
from audit.models.constants import RESUBMISSION_STATUS
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from config.settings import (
    STATE_ABBREVS,
    SUMMARY_REPORT_DOWNLOAD_LIMIT,
    FINDINGS_SUMMARY_REPORT_DOWNLOAD_LIMIT,
)
from dissemination.forms.search_forms import AdvancedSearchForm, SearchForm
from dissemination.search import gather_errors
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

from audit.models.constants import RESUBMISSION_STATUS

def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def compute_resubmission_tag(row):
    """
    Return: "Most Recent" | "Resubmitted" | None

    Rules:
      - Show a tag ONLY if it has resubmission_meta (i.e., it is a resubmission).
      - MOST_RECENT  -> "Most Recent"
      - ORIGINAL/DEPRECATED -> "Resubmitted"
      - Legacy (no resubmission_meta) -> None
    """
    meta = _get(row, "resubmission_meta") or None
    if not meta:
        return None  # legacy or never-resubmitted

    status = meta.get("resubmission_status")
    if status == RESUBMISSION_STATUS.MOST_RECENT:
        return "Most Recent"
    if status in (RESUBMISSION_STATUS.ORIGINAL, RESUBMISSION_STATUS.DEPRECATED):
        return "Resubmitted"
    return None

def populate_resubmission_tag(paginator_page):
    for row in paginator_page.object_list:
        tag = compute_resubmission_tag(row)
        try:
            setattr(row, "resubmission_tag", tag)  # model instance
        except Exception:
            row["resubmission_tag"] = tag          # dict row
    return paginator_page


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
                "findings_report_download_limit": FINDINGS_SUMMARY_REPORT_DOWNLOAD_LIMIT,
            },
        )

    @newrelic_timing_metric("search-advanced")
    def post(self, request, *args, **kwargs):
        """
        When accessing the search page through post, run a search and display the results.
        """
        time_starting_post = time.time()

        form = AdvancedSearchForm(request.POST)
        advanced_search_flag = True
        paginator_results = None
        results_count = None
        page = 1
        results = []
        context = {
            "advanced_search_flag": advanced_search_flag,  # Render advanced search filters
            "include_private": include_private_results(request),
            "state_abbrevs": STATE_ABBREVS,
            "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
            "findings_report_download_limit": FINDINGS_SUMMARY_REPORT_DOWNLOAD_LIMIT,
        }

        # Obtain cleaned form data.
        form.is_valid()  # Runs default cleaning functions AND "clean_*" functions in forms.py
        form_data = form.cleaned_data
        form_data["advanced_search_flag"] = advanced_search_flag
        form_user_input = {k: v[0] if len(v) == 1 else v for k, v in form.data.lists()}

        # The form contains an error list. Gather custom error messages for certain fields.
        context["errors"] = gather_errors(form)

        # If the form failed to validate, don't search and return early with error messages.
        if not form.is_valid():
            return render(
                request,
                "search.html",
                context
                | {
                    "form": form,
                    "form_user_input": form_user_input,
                },
            )

        logger.info(f"Advanced searching on fields: {form_data}")

        # Generate results on valid user input.
        results = run_search(form_data)
        results_count = results.count()

        # Reset page number to one if the value already surpasses the number of feasible pages.
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

        # If there are results, populate the agency name in cog/over field
        if results_count > 0:
            paginator_results = populate_cog_over_name(paginator_results)
            paginator_results = populate_resubmission_tag(paginator_results)


        context = context | {
            "form_user_input": form_user_input,
            "form": form,
            "limit": form_data["limit"],
            "order_by": form_data["order_by"],
            "order_direction": form_data["order_direction"],
            "page": page,
            "results_count": results_count,
            "results": paginator_results,
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
                "findings_report_download_limit": FINDINGS_SUMMARY_REPORT_DOWNLOAD_LIMIT,
            },
        )

    @newrelic_timing_metric("search")
    def post(self, request, *args, **kwargs):
        """
        When accessing the search page through post, run a search and display the results.
        """
        time_starting_post = time.time()

        form = SearchForm(request.POST)
        advanced_search_flag = False
        paginator_results = None
        results_count = None
        page = 1
        results = []
        context = {
            "advanced_search_flag": advanced_search_flag,  # Render only basic search filters
            "include_private": include_private_results(request),
            "state_abbrevs": STATE_ABBREVS,
            "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
            "findings_report_download_limit": FINDINGS_SUMMARY_REPORT_DOWNLOAD_LIMIT,
        }

        # Obtain cleaned form data.
        form.is_valid()  # Runs default cleaning functions AND "clean_*" functions in forms.py
        form_data = form.cleaned_data
        form_data["advanced_search_flag"] = advanced_search_flag
        form_user_input = {k: v[0] if len(v) == 1 else v for k, v in form.data.lists()}

        # The form contains an error list. Gather custom error messages for certain fields.
        context["errors"] = gather_errors(form)

        # If the form failed to validate, don't search and return early with error messages.
        if not form.is_valid():
            return render(
                request,
                "search.html",
                context
                | {
                    "form": form,
                    "form_user_input": form_user_input,
                },
            )

        logger.info(f"Searching on fields: {form_data}")

        # Generate results on valid user input.
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

        # If there are results, populate the agency name in cog/over field
        if results_count > 0:
            paginator_results = populate_cog_over_name(paginator_results)
            paginator_results = populate_resubmission_tag(paginator_results)


        context = context | {
            "form_user_input": form_user_input,
            "form": form,
            "limit": form_data["limit"],
            "order_by": form_data["order_by"],
            "order_direction": form_data["order_direction"],
            "page": page,
            "results_count": results_count,
            "results": paginator_results,
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
            "search-audit.html",
            {
                "is_beta": True,
                "non_beta_url": "dissemination:Search",
                "form": form,
                "form_user_input": {"audit_year": default_checked_audit_years},
                "state_abbrevs": STATE_ABBREVS,
                "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
                "findings_report_download_limit": FINDINGS_SUMMARY_REPORT_DOWNLOAD_LIMIT,
            },
        )

    @newrelic_timing_metric("search-audit")
    def post(self, request, *args, **kwargs):
        """
        When accessing the search page through post, run a search and display the results.
        """
        time_starting_post = time.time()

        form = AdvancedSearchForm(request.POST)
        advanced_search_flag = True
        paginator_results = None
        results_count = None
        page = 1
        context = {
            "advanced_search_flag": advanced_search_flag,  # Render advanced search filters
            "include_private": include_private_results(request),
            "state_abbrevs": STATE_ABBREVS,
            "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
            "findings_report_download_limit": FINDINGS_SUMMARY_REPORT_DOWNLOAD_LIMIT,
        }

        # Obtain cleaned form data.
        form.is_valid()  # Runs default cleaning functions AND "clean_*" functions in forms.py
        form_data = form.cleaned_data
        form_data["advanced_search_flag"] = advanced_search_flag
        form_user_input = {k: v[0] if len(v) == 1 else v for k, v in form.data.lists()}

        # The form contains an error list. Gather custom error messages for certain fields.
        context["errors"] = gather_errors(form)

        # If the form failed to validate, don't search and return early with error messages.
        if not form.is_valid():
            return render(
                request,
                "search.html",
                context
                | {
                    "form": form,
                    "form_user_input": form_user_input,
                },
            )

        logger.info(f"Searching on fields: {form_data}")

        # Generate results on valid user input.
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
        if results_count > 0:
            paginator_results = audit_populate_cog_over_name(paginator_results)
            paginator_results = populate_resubmission_tag(paginator_results)

        context = context | {
            "form_user_input": form_user_input,
            "form": form,
            "limit": form_data["limit"],
            "order_by": form_data["order_by"],
            "order_direction": form_data["order_direction"],
            "page": page,
            "results_count": results_count,
            "results": paginator_results,
        }
        time_beginning_render = time.time()
        total_time_ms = int(
            math.ceil((time_beginning_render - time_starting_post) * 1000)
        )
        total_time_s = total_time_ms / 1000
        logger.info(f"Total time between post and render {total_time_ms}ms")
        return render(
            request, "search-audit.html", context | {"total_time_s": total_time_s}
        )
