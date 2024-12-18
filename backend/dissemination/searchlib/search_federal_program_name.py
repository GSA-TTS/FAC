from django.db.models import Q
import time
from .search_general import report_timing

import logging

logger = logging.getLogger(__name__)


def search_federal_program_name(general_results, params):
    """
    Searches on Federal Award field 'federal_program_name'.
    """
    t0 = time.time()
    q = Q()
    names = params.get("federal_program_name", [])

    if not names:
        return general_results

    for name in names:
        q.add(Q(federal_program_name__icontains=name), Q.OR)

    filtered_general_results = general_results.filter(q).distinct()

    t1 = time.time()
    report_timing("federal_program_name", params, t0, t1)

    return filtered_general_results
