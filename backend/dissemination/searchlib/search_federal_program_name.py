from .search_general import report_timing
from .search_constants import text_input_delimiters

from django.db.models import Q

import logging
import time


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
        q_sub = Q()

        for sub in _split(name, text_input_delimiters):
            q_sub.add(Q(federal_program_name__icontains=sub), Q.AND)

        q.add(q_sub, Q.OR)

    filtered_general_results = general_results.filter(q).distinct()

    t1 = time.time()
    report_timing("federal_program_name", params, t0, t1)

    return filtered_general_results


def _split(text, delimiters):
    """
    Functions the same as string.split, but accepts a list of delimiters
    """
    if not delimiters:
        return text

    default_delimiter = delimiters[0]

    # Skip delimiters[0] because it splits on that at the end
    for delimiter in delimiters[1:]:
        text = text.replace(delimiter, default_delimiter)

    return [i.strip() for i in text.split(default_delimiter)]
