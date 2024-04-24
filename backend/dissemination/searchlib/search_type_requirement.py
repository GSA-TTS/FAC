from django.db.models import Q
import time
from .search_general import report_timing

import logging

logger = logging.getLogger(__name__)


def search_type_requirement(general_results, params):
    """
    Searches on Finding field 'type_requirement'. One or several of ~550 combinations.
    """
    t0 = time.time()
    q = Q()
    type_requirements = params.get("type_requirement", [])

    for tr in type_requirements:
        q |= Q(type_requirement=tr)
    filtered_general_results = general_results.filter(q).distinct()

    t1 = time.time()
    report_timing("search_type_requirement", params, t0, t1)
    return filtered_general_results
