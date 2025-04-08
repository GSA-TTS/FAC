from django.db.models import Q

from dissemination.searchlib.search_constants import SearchFields


def audit_search_uei_ein(params):
    uei_eins = params.get(SearchFields.uei_ein.value)
    uei_ein_query = Q()
    uei_ein_query |= Q(auditee_ein__in=uei_eins) | Q(auditee_uei__in=uei_eins)

    for uei_ein in uei_eins:
        uei_ein_query |= Q(additional_eins__icontains=uei_ein) | Q(
            additional_ueis__icontains=uei_ein
        )

    return uei_ein_query if uei_eins else Q()
