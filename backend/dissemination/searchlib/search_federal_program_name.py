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
