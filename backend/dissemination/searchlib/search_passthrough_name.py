from django.db.models import Q
import time
from .search_general import report_timing

import logging

logger = logging.getLogger(__name__)


def search_passthrough_name(general_results, params):
    """
    Searches on Passthrough field 'passthrough_name'.
    """
    t0 = time.time()
    q = Q()
    passthrough_names = params.get("passthrough_name", [])

    if not passthrough_names:
        return general_results

    for term in passthrough_names:
        q_sub = Q()
        for sub in term.split():
            q_sub.add(Q(passthrough_name__icontains=sub), Q.AND)
        q.add(q_sub, Q.OR)
    
    filtered_general_results = general_results.filter(q).distinct()

    t1 = time.time()
    report_timing("search_passthrough_name", params, t0, t1)
    return filtered_general_results
