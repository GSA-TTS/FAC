from django.db.models import Q
import time
from .search_general import report_timing

import logging

logger = logging.getLogger(__name__)


def search_major_program(general_results, params):
    """
    Searches on FederalAward columns 'is_major'. Comes in as True/False, to search on Y/N.
    """
    t0 = time.time()
    q = Q()
    major_program_fields = params.get("major_program", [])

    if "True" in major_program_fields:
        q |= Q(is_major="Y")
    elif "False" in major_program_fields:
        q |= Q(is_major="N")

    filtered_general_results = general_results.filter(q).distinct()

    t1 = time.time()
    report_timing("search_major_program", params, t0, t1)
    return filtered_general_results
