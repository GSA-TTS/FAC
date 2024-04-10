import time
from math import ceil
import logging
from django.db.models import Q

logger = logging.getLogger(__name__)


def search_general(base_model, params=None):
    params = params or dict()
    # Time general reduction
    t0 = time.time()

    ##############
    # Initialize query.
    r_base = base_model.objects.all()

    ##############
    # Audit years
    # query.add(_get_audit_years_match_query(audit_years), Q.AND)
    q_audit_year = _get_audit_years_match_query(params.get("audit_years", None))
    r_audit_year = base_model.objects.filter(q_audit_year)

    ##############
    # State
    q_state = _get_auditee_state_match_query(params.get("auditee_state", None))
    r_state = base_model.objects.filter(q_state)

    ##############
    # Names
    q_names = _get_names_match_query(params.get("names", None))
    r_names = base_model.objects.filter(q_names)

    ##############
    # UEI/EIN
    q_uei = _get_uei_or_eins_match_query(params.get("uei_or_eins", None))
    r_uei = base_model.objects.filter(q_uei)

    ##############
    # Start/end dates
    q_start_date = _get_start_date_match_query(params.get("start_date", None))
    r_start_date = base_model.objects.filter(q_start_date)
    q_end_date = _get_end_date_match_query(params.get("end_date", None))
    r_end_date = base_model.objects.filter(q_end_date)

    ##############
    # Cog/Over
    q_cogover = _get_cog_or_oversight_match_query(
        params.get("agency_name", None), params.get("cog_or_oversight", None)
    )
    r_cogover = base_model.objects.filter(q_cogover)

    ##############
    # Intersection
    # Intersection on result sets is an &.
    results = (
        r_audit_year
        & r_start_date
        & r_end_date
        & r_state
        & r_cogover
        & r_names
        & r_uei
        & r_base
    )

    t1 = time.time()
    report_timing("search_general", params, t0, t1)
    return results


def report_timing(tag, params, start, end):
    readable = int(ceil((end - start) * 1000))
    logger.info(f"SEARCH_TIMING {hex(id(params))[8:]} {tag} {readable}ms")


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


def _get_auditee_state_match_query(auditee_state):
    if not auditee_state:
        return Q()

    return Q(auditee_state__in=[auditee_state])


def _get_names_match_query(names_list):
    """
    Given a list of (potential) names, return the query object that searches auditee and firm names.
    """
    if not names_list:
        return Q()

    name_fields = [
        # "auditee_city",
        "auditee_contact_name",
        "auditee_certify_name",
        "auditee_email",
        "auditee_name",
        # "auditee_state",
        # "auditor_city",
        "auditor_contact_name",
        "auditor_certify_name",
        "auditor_email",
        "auditor_firm_name",
        # "auditor_state",
    ]

    names_match = Q()

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

    # Now, for each field (e.g. "auditee_contact_name")
    # build up an AND over the terms. We want something where all of the
    # terms appear.
    # Then, do an OR over all of the fields. If that combo appears in
    # any of the fields, we want to return it.
    for field in name_fields:
        field_q = Q()
        for name in flattened:
            field_q.add(Q(**{f"{field}__icontains": name}), Q.AND)
        names_match.add(field_q, Q.OR)

    # Now, "college berea" and "university state ohio" return
    # the appropriate terms. It is also significantly faster than what
    # we had before.

    return names_match
