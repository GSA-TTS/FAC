from django.db.models import Q

from dissemination.models import General, FederalAward


def search_general(
    alns=None,
    names=None,
    uei_or_eins=None,
    start_date=None,
    end_date=None,
    cog_or_oversight=None,
    agency_name=None,
    audit_years=None,
):
    query = Q(is_public=True)

    if alns:
        query.add(_get_aln_match_query(alns), Q.AND)

    if names:
        query.add(_get_names_match_query(names), Q.AND)

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
        if cog_or_oversight.lower() == "cog":
            cog_match = Q(cognizant_agency__in=[agency_name])
            query.add(cog_match, Q.AND)
        elif cog_or_oversight.lower() == "oversight":
            oversight_match = Q(oversight_agency__in=[agency_name])
            query.add(oversight_match, Q.AND)

    if audit_years:
        fiscal_year_match = Q(audit_year__in=audit_years)
        query.add(fiscal_year_match, Q.AND)

    results = General.objects.filter(query).order_by("-fac_accepted_date")

    return results


def _get_aln_match_query(alns):
    """
    Create the match query for ALNs. d
    Takes: A list of (potential) ALNs.
    Returns: A query object matching on relevant report_ids found in the FederalAward table.

    # ALNs are a little weird, because they are stored per-award in the FederalAward table. To search on ALNs, we:
    # 1. Split the given ALNs into a list with their prefix and extention.
    # 2. Search the FederalAward table for awards with matching federal_agency_prefix and federal_award_extension.
    # 3. Add the report_ids from the identified awards to the search params.
    """
    # Split each ALN into [prefix, extention]
    split_alns = []
    for aln in alns:
        split_aln = aln.split(".")
        if len(split_aln) == 2:
            split_alns.append(split_aln)
    # Search for relevant awards
    report_ids = []
    for aln_list in split_alns:
        matching_awards = FederalAward.objects.filter(
            federal_agency_prefix=aln_list[0], federal_award_extension=aln_list[1]
        ).values()
        if matching_awards:
            report_ids.append(matching_awards[0].get("report_id"))
    # Add the report_id's from the award search to the full search params
    alns_match = Q()
    for report_id in report_ids:
        alns_match.add(Q(report_id=report_id), Q.OR)
    return alns_match


def _get_names_match_query(names):
    """
    Given a list of (potential) names, return the query object that searches auditee and firm names.
    """
    names_match = Q()
    for name in names:
        names_match.add(Q(auditee_name__search=name), Q.OR)
        names_match.add(Q(auditor_firm_name__search=name), Q.OR)
    return names_match
