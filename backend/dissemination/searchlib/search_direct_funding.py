from django.db.models import Q
import time
from .search_general import report_timing

import logging

logger = logging.getLogger(__name__)


def audit_search_direct_funding(params):
    q = Q()
    direct_funding_fields = params.get("direct_funding")
    for field in direct_funding_fields:
        match field:
            case "direct_funding":
                q |= Q(has_direct_funding=True)
            case "passthrough_funding":
                q |= Q(has_indirect_funding=False)
            case _:
                pass
    return q


# TODO: Update Post SOC Launch -> Remove unused
def search_direct_funding(general_results, params):
    t0 = time.time()
    q = Q()
    direct_funding_fields = params.get("direct_funding", [])

    for field in direct_funding_fields:
        match field:
            case "direct_funding":
                q |= Q(is_direct="Y")
            case "passthrough_funding":
                q |= Q(is_direct="N")
            case _:
                pass

    filtered_general_results = general_results.filter(q)

    t1 = time.time()
    report_timing("search_direct_funding", params, t0, t1)
    return filtered_general_results
