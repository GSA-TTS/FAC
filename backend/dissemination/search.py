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
    include_private=False,
):
    query = Q()

    query.add(_get_is_public_query(include_private), Q.AND)
    query.add(_get_aln_match_query(alns), Q.AND)
    query.add(_get_names_match_query(names), Q.AND)
    query.add(_get_uei_or_eins_match_query(uei_or_eins), Q.AND)
    query.add(_get_start_date_match_query(start_date), Q.AND)
    query.add(_get_end_date_match_query(end_date), Q.AND)
    query.add(_get_cog_or_oversight_match_query(agency_name, cog_or_oversight), Q.AND)
    query.add(_get_audit_years_match_query(audit_years), Q.AND)

    results = General.objects.filter(query).order_by("-fac_accepted_date")

    return results


def _get_is_public_query(include_private):
    if not include_private:
        return Q(is_public=True)
    return Q()


def _get_aln_match_query(alns):
    """
    Create the match query for ALNs.
    Takes: A list of (potential) ALNs.
    Returns: A query object matching on relevant report_ids found in the FederalAward table.

    # ALNs are a little weird, because they are stored per-award in the FederalAward table. To search on ALNs, we:
    # 1. Split the given ALNs into a set with their prefix and extention.
    # 2. Search the FederalAward table for awards with matching federal_agency_prefix and federal_award_extension.
    #    If there's just a prefix, search on all prefixes.
    #    If there's a prefix and extention, search on both.
    # 3. Add the report_ids from the identified awards to the search params.
    """

    if not alns:
        return Q()

    # Split each ALN into (prefix, extention)
    split_alns = set()
    agency_numbers = set()
    for aln in alns:
        if len(aln) == 2:
            # If we don't wrap the `aln` with [], the string
            # goes in as individual characters. A weirdness of Python sets.
            agency_numbers.update([aln])
        else:
            split_aln = aln.split(".")
            if len(split_aln) == 2:
                # The [wrapping] is so the tuple goes into the set as a tuple.
                # Otherwise, the individual elements go in unpaired.
                split_alns.update([tuple(split_aln)])

    # Search for relevant awards
    report_ids = _get_aln_report_ids(split_alns)

    for agency_number in agency_numbers:
        matching_awards = FederalAward.objects.filter(
            federal_agency_prefix=agency_number
        ).values()
        if matching_awards:
            for matching_award in matching_awards:
                report_ids.update([matching_award.get("report_id")])
    # Add the report_id's from the award search to the full search params
    alns_match = Q()
    for report_id in report_ids:
        alns_match.add(Q(report_id=report_id), Q.OR)
    return alns_match


def _get_aln_report_ids(split_alns):
    """
    Given a set of split ALNs, find the relevant awards and return their report_ids.
    """
    report_ids = set()
    for aln_list in split_alns:
        matching_awards = FederalAward.objects.filter(
            federal_agency_prefix=aln_list[0], federal_award_extension=aln_list[1]
        ).values()
        if matching_awards:
            for matching_award in matching_awards:
                # Again, adding in a string requires [] so the individual
                # characters of the report ID don't go in... we want the whole string.
                report_ids.update([matching_award.get("report_id")])
    return report_ids


def _get_names_match_query(names):
    """
    Given a list of (potential) names, return the query object that searches auditee and firm names.
    """
    if not names:
        return Q()

    name_fields = [
        "auditee_city",
        "auditee_contact_name",
        "auditee_email",
        "auditee_name",
        "auditee_state",
        "auditor_city",
        "auditor_contact_name",
        "auditor_email",
        "auditor_firm_name",
        "auditor_state",
    ]

    names_match = Q()

    # turn ["name1", "name2", "name3"] into "name1 name2 name3"
    names = " ".join(names)
    for field in name_fields:
        names_match.add(Q(**{"%s__search" % field: names}), Q.OR)

    return names_match


def _get_uei_or_eins_match_query(uei_or_eins):
    if not uei_or_eins:
        return Q()

    uei_or_ein_match = Q(
        Q(auditee_uei__in=uei_or_eins) | Q(auditee_ein__in=uei_or_eins)
    )
    return uei_or_ein_match


def _get_start_date_match_query(start_date):
    if not start_date:
        return Q()

    return Q(fac_accepted_date__gte=start_date)


def _get_end_date_match_query(end_date):
    if not end_date:
        return Q()

    return Q(fac_accepted_date__lte=end_date)


def _get_cog_or_oversight_match_query(agency_name, cog_or_oversight):
    if not cog_or_oversight:
        return Q()

    if cog_or_oversight.lower() == "cog":
        return Q(cognizant_agency__in=[agency_name])
    elif cog_or_oversight.lower() == "oversight":
        return Q(oversight_agency__in=[agency_name])


def _get_audit_years_match_query(audit_years):
    if not audit_years:
        return Q()

    return Q(audit_year__in=audit_years)
