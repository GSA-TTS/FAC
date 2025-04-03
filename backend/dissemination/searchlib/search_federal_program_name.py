from .search_constants import text_input_delimiters

from django.db.models import Q

import re


def audit_search_federal_program_name(params):
    query = Q()
    names = params.get("federal_program_name")
    for name in names:
        sub_query = Q()
        rsplit = re.compile("|".join(text_input_delimiters)).split

        for sub in [s.strip() for s in rsplit(name)]:
            sub_query.add(Q(program_names__icontains=sub), Q.AND)

        query.add(sub_query, Q.OR)
    return query


# TODO: Update Post SOC Launch -> Remove unused
def search_federal_program_name(general_results, params):
    """
    Searches on Federal Award field 'federal_program_name'.
    """
    query = Q()
    names = params.get("federal_program_name", [])

    if not names:
        return general_results

    for name in names:
        sub_query = Q()
        rsplit = re.compile("|".join(text_input_delimiters)).split

        for sub in [s.strip() for s in rsplit(name)]:
            sub_query.add(Q(federal_program_name__icontains=sub), Q.AND)

        query.add(sub_query, Q.OR)

    filtered_general_results = general_results.filter(query).distinct()

    return filtered_general_results
