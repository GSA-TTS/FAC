from .search_general import report_timing

from django.db.models import Q

import logging
import time

logger = logging.getLogger(__name__)


def audit_search_cog_or_oversight(params):
    cog_over_number = params.get("cog_over_number", None)
    cog_or_oversight = params.get("cog_or_oversight", None)
    if cog_or_oversight.lower() in ["", "either"]:
        if cog_over_number:
            return Q(
                Q(cognizant_agency__in=[cog_over_number])
                | Q(oversight_agency__in=[cog_over_number])
            )
        else:
            # Every submission should have a value for either cog or over, so
            # nothing to do here
            return Q()
    elif cog_or_oversight.lower() == "cog":
        if cog_over_number:
            return Q(cognizant_agency__in=[cog_over_number])
        else:
            # Submissions that have any cog
            return Q(cognizant_agency__isnull=False)
    elif cog_or_oversight.lower() == "oversight":
        if cog_over_number:
            return Q(oversight_agency__in=[cog_over_number])
        else:
            # Submissions that have any over
            return Q(oversight_agency__isnull=False)


# TODO: Update Post SOC Launch -> Remove unused
def search_cog_or_oversight(general_results, params):
    t0 = time.time()

    q_cogover = _get_cog_or_oversight_match_query(
        params.get("cog_over_number", None), params.get("cog_or_oversight", "either")
    )
    filtered_general_results = general_results.filter(q_cogover)

    t1 = time.time()
    report_timing("search_cog_or_oversight", params, t0, t1)

    return filtered_general_results


def _get_cog_or_oversight_match_query(cog_over_number, cog_or_oversight):
    if cog_or_oversight.lower() in ["", "either"]:
        if cog_over_number:
            return Q(
                Q(cognizant_agency__in=[cog_over_number])
                | Q(oversight_agency__in=[cog_over_number])
            )
        else:
            # Every submission should have a value for either cog or over, so
            # nothing to do here
            return Q()
    elif cog_or_oversight.lower() == "cog":
        if cog_over_number:
            return Q(cognizant_agency__in=[cog_over_number])
        else:
            # Submissions that have any cog
            return Q(cognizant_agency__isnull=False)
    elif cog_or_oversight.lower() == "oversight":
        if cog_over_number:
            return Q(oversight_agency__in=[cog_over_number])
        else:
            # Submissions that have any over
            return Q(oversight_agency__isnull=False)
