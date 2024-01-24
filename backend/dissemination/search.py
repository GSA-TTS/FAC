from django.db.models import Q, Count
from collections import namedtuple as NT
from dissemination.models import General, FederalAward
import logging
import time
from .search_general import (
    report_timing,
    search_general
    )
from .search_alns import (
    search_alns
)

logger = logging.getLogger(__name__)
ALN = NT("ALN", "prefix, program")

DAS_LIMIT=1000

class ORDER_BY:
    fac_accepted_date = "fac_accepted_date"
    auditee_name = "auditee_name"
    auditee_uei = "auditee_uei"
    audit_year = "audit_year"
    cog_over = "cog_over"
    findings_my_aln = "findings_my_aln"
    findings_all_aln = "findings_all_aln"


class DIRECTION:
    ascending = "ascending"
    descending = "descending"


#######################
# https://books.agiliq.com/en/latest/README.html
# Their ORM cookbook looks to be useful reading.
# https://books.agiliq.com/projects/django-orm-cookbook/en/latest/subquery.html

def search(params):
    """
    Given any (or no) search fields, build and execute a query on the General table and return the results.
    Empty searches return everything.
    """
    ##############
    # Set defaults for things we definitely want in the params.
    params = _set_general_defaults(params)

    # Time the whole thing.
    t0 = time.time()

    ##############
    # GENERAL
    results = search_general(params)

    ##############
    # Truncate down to the limit
    # This is the stopgap. If we have too many still, we're going
    # to force the issue and truncate the result set.
    # https://docs.djangoproject.com/en/4.2/topics/db/queries/#limiting-querysets
    results = results[:DAS_LIMIT]

    results = search_alns(results, params)

    results = _order_results(results, params)
    
    t1 = time.time()
    report_timing("search", params, t0, t1)
    return results

def _set_general_defaults(params):
    #############
    # Set some defaults.

    # Let's make sure we have a confirmation that
    # we default to not sharing data marked as suppressed.
    if not params.get("include_private"):
        params["include_private"] = False

    # Set default order direction
    if not params.get("order_by", None):
        params["order_by"] = ORDER_BY.fac_accepted_date
    if not params.get("order_direction", None):
        params["order_direction"] = DIRECTION.descending

    return params

def _order_results(results, params):
    t0 = time.time()
    if params.get("order_by") == ORDER_BY.findings_my_aln:
        results = sorted(
            results,
            key=lambda obj: obj.finding_my_aln,
            reverse=bool(params.get("order_direction") == DIRECTION.descending),
        )
    elif params.get("order_by") == ORDER_BY.findings_all_aln:
        results = sorted(
            results,
            key=lambda obj: obj.finding_all_aln,
            reverse=bool(params.get("order_direction") == DIRECTION.descending),
        )
    t1 = time.time()
    report_timing("_order_results", params, t0, t1)
    return results

def _sort_results(results, order_direction, order_by):
    # Instead of nesting conditions, we'll prep a string
    # for determining the sort direction.
    match order_direction:
        case DIRECTION.ascending:
            direction = ""
        case _:
            direction = "-"

    # Now, apply the sort that we pass in front the front-end.
    match order_by:
        case ORDER_BY.auditee_name:
            results = results.order_by(f"{direction}auditee_name")
        case ORDER_BY.auditee_uei:
            results = results.order_by(f"{direction}auditee_uei")
        case ORDER_BY.fac_accepted_date:
            results = results.order_by(f"{direction}fac_accepted_date")
        case ORDER_BY.audit_year:
            results = results.order_by(f"{direction}audit_year")
        case ORDER_BY.cog_over:
            if order_direction == DIRECTION.ascending:
                results = results.order_by("cognizant_agency")
            else:
                results = results.order_by("oversight_agency")
        case _:
            results = results.order_by(f"{direction}fac_accepted_date")

    return results


def _split_alns(alns):
    """
    Split an ALN query string into two sets.
        1. split_alns: {(federal_agency_prefix, federal_award_extension), ...}
        2. agency_numbers: {('federal_agency_prefix'), ...}
    """
    split_alns = set()
    for aln in alns:
        if len(aln) == 2:
            # If we don't wrap the `aln` with [], the string
            # goes in as individual characters. A weirdness of Python sets.
            split_alns.update([ALN(aln, None)])
        else:
            split_aln = aln.split(".")
            if len(split_aln) == 2:
                # The [wrapping] is so the tuple goes into the set as a tuple.
                # Otherwise, the individual elements go in unpaired.
                # split_alns.update([tuple(split_aln)])
                split_alns.update([ALN(split_aln[0], split_aln[1])])
    return split_alns


def _get_aln_report_ids(split_alns):
    """
    Given a set of ALNs and a set agency numbers, find the relevant awards and return a set of report_ids.
    Utilizing sets helps to avoid duplicate reports.
    """
    report_ids = set()
    # Matching on a specific ALN, such as '12.345'
    for aln in split_alns:
        if aln.program:
            matching_awards = FederalAward.objects.filter(
                federal_agency_prefix=aln.prefix, federal_award_extension=aln.program
            ).values()
            if matching_awards:
                for matching_award in matching_awards:
                    # Again, adding in a string requires [] so the individual
                    # characters of the report ID don't go in... we want the whole string.
                    report_ids.update([matching_award.get("report_id_id")])
        else:
            # logger.info(f"Checking agency number {agency_number}")
            matching_awards = FederalAward.objects.filter(
                federal_agency_prefix=aln.prefix
            ).values()
            # logger.info(f"Matching awards for {agency_number}: {matching_awards}")
            if matching_awards:
                for matching_award in matching_awards:
                    # We have a foreign key now... this needs to be report_id_id...
                    report_ids.update([matching_award.get("report_id_id")])

    return report_ids


def _attach_finding_my_aln_and_finding_all_aln_fields(
    results, split_alns
):
    """
    Given the results QuerySet (full of 'General' objects) and an ALN query string,
    return a list of 'General' objects, where each object has two new fields.

    The process:
    1. Pull the results report_ids into a list.
    2. Construct queries for my_aln vs all_aln
        a. aln_q - All awards with findings under the given ALNs
        b. not_aln_q - All awards with findings under NOT the given ALNs
    2. Make the two queries for FederalAwards, 'finding_on_my_alns' and 'finding_on_all_alns'. Ensure results are under the given report_ids.
    3. For every General under results, we check:
        a. If a FederalAward in 'finding_on_my_alns' has a report_id under this General, finding_my_aln = True
        b. If a FederalAward in 'finding_all_my_alns' has a report_id under this General, finding_all_aln = True
    4. Return the updated results QuerySet.
    """
    logger.info(f"_afmafaaf start")
    t0 = time.time()
    # report_ids = list(results.values_list("report_id", flat=True))
    t1 = time.time()
    logger.info(f"_afmafaaf t1-t0: {t1-t0}")
    agency_numbers = list(filter(lambda sa: not sa.program, split_alns))

    aln_q = Q()
    for aln in split_alns:
        aln_q.add(
            Q(federal_agency_prefix=aln.prefix)
            & Q(federal_award_extension=aln.program),
            Q.OR,
        )
    for agency in agency_numbers:
        aln_q.add(Q(federal_agency_prefix=agency), Q.OR)

    not_aln_q = Q()
    for aln in split_alns:
        not_aln_q.add(
            ~(
                Q(federal_agency_prefix=aln.prefix)
                & Q(federal_award_extension=aln.program)
            ),
            Q.AND,
        )
    not_aln_q.add(~Q(federal_agency_prefix__in=list(agency_numbers)), Q.AND)
    
    t1a = time.time()
    logger.info(f"_afmafaaf t1a-t1: {t1a-t1}")
    t2 = time.time()    

    finding_on_my_alns = FederalAward.objects.filter(
        aln_q,
        report_id__in=results,
        findings_count__gt=0,
    )
    finding_on_any_aln = FederalAward.objects.filter(
        not_aln_q,
        report_id__in=results,
        findings_count__gt=0,
    )

    logger.info(f"_afmafaaf t2-t1: {t2-t1a}")
    t3 = time.time()    

    for general in results:
        general.finding_my_aln = False
        general.finding_all_aln = False
        for relevant_award in finding_on_my_alns:
            if relevant_award.report_id == general.report_id:
                general.finding_my_aln = True
        for relevant_award in finding_on_any_aln:
            if relevant_award.report_id == general.report_id:
                general.finding_all_aln = True
    
    t4 = time.time()
    logger.info(f"_afmafaaf t4-t3: {t4-t3}")
    logger.info(f"_afmafaaf t4-t0: {t4-t0}")
    return results

import itertools

def _get_aln_match_query(split_alns, limit=DAS_LIMIT):
    """
    Given split ALNs and agency numbers, return the match query for ALNs.
    """
    # Search for relevant awards
    report_ids = _get_aln_report_ids(split_alns)

    # Add the report_id's from the award search to the full search params
    alns_match = Q()
    limited_report_ids = set(itertools.islice(report_ids, limit))
    # for report_id in limited_report_ids:
    #     alns_match.add(Q(report_id=report_id), Q.OR)
    alns_match = Q(report_id__in=limited_report_ids)

    return alns_match


