from django.db.models import Q
import time
from .search_general import report_timing

import logging

logger = logging.getLogger(__name__)


def search_major_program(general_results, params):
    """
    Searches on FederalAward columns 'is_major' and 'audit_report_type'.
    If 'any', just look for 'is_major' to be Y.
    If 'A'/'D'/'Q'/'U', look for both 'is_major' to be Y and 'audit_report_type' to be one of the given values.
    """
    t0 = time.time()
    q = Q()
    major_program_fields = params["major_program"]

    if "any" in major_program_fields:
        q |= Q(federalaward__is_major="Y")
    else:
        for field in major_program_fields:
            q |= Q(federalaward__is_major="Y", federalaward__audit_report_type=field)

    filtered_general_results = general_results.filter(q).distinct()

    t1 = time.time()
    report_timing("search_major_program", params, t0, t1)
    return filtered_general_results
