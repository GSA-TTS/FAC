from django.db.models import Q

from dissemination.models import General


def search_general(
    names, uei_or_eins, start_date, end_date, cog_or_oversight, agency_name
):
    query = Q(is_public=True)

    # TODO: use something like auditee_name__contains
    # SELECT * WHERE auditee_name LIKE '%SomeString%'
    if names:
        names_match = Q(Q(auditee_name__in=names) | Q(auditor_firm_name__in=names))
        query.add(names_match, Q.AND)

    if uei_or_eins:
        uei_or_ein_match = Q(
            Q(auditee_uei__in=uei_or_eins) | Q(auditee_ein__in=uei_or_eins)
        )
        query.add(uei_or_ein_match, Q.AND)

    if start_date:
        start_date_match = Q(fac_accepted_date__gte=start_date)
        query.add(start_date_match, Q.AND)

    if end_date:
        end_date_match = Q(fac_accepted_date__lte=end_date)
        query.add(end_date_match, Q.AND)

    if cog_or_oversight:
        if cog_or_oversight == "Cognizant":
            cog_match = Q(cognizant_agency__in=[agency_name])
            query.add(cog_match, Q.AND)
        elif cog_or_oversight == "Oversight":
            oversight_match = Q(oversight_agency__in=[agency_name])
            query.add(oversight_match, Q.AND)

    results = General.objects.filter(query)

    return results
