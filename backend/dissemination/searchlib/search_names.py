from django.db.models import Q

from dissemination.searchlib.search_constants import SearchFields


def audit_search_names(params):
    names_list = params.get(SearchFields.names.value)

    # The search terms are coming in as a string in a list.
    # E.g. the search text "college berea" returns nothing,
    # when it should return entries for "Berea College". That is
    # because it comes in as
    # ["college berea"]
    #
    # This has to be flattened to a list of singleton terms.
    flattened = []
    for term in names_list:
        for sub in term.split():
            flattened.append(sub)

    query = Q()
    for name in flattened:
        query |= Q(search_names__icontains=name)
    return query if flattened else Q()
