from django.db.models import Q, Subquery
from collections import namedtuple as NT
from dissemination.models import FederalAward
import time
from .search_general import (
    report_timing
    )

from .search_constants import (
    ORDER_BY,
    DIRECTION,
)

import logging
import operator

logger = logging.getLogger(__name__)

ALN = NT("ALN", "prefix, program")

def search_alns(results, params):
    t0 = time.time()
    full_alns = _get_full_alns(params)
    agency_numbers = _get_agency_numbers(params)

    if not (full_alns or agency_numbers):
        return results
    else:
        r_all_alns = _gather_results_for_all_alns(full_alns, agency_numbers)
        all_alns_count = r_all_alns.count()
        logger.info(f"search_alns matching FederalAward rows[{all_alns_count}]")
        results = results.filter(report_id__in=Subquery(r_all_alns.values_list('report_id'))) #_id_id
        logger.info(f"search_alns general rows[{results.count()}]")
        results = _annotate_findings(results, params, r_all_alns)
        results = _findings_sort(results, params)

        t1 = time.time()
        report_timing("search_alns", params, t0, t1)
        return results

def _findings_sort(results, params):
    if params.get("order_by") == ORDER_BY.findings_my_aln:
        results = sorted(
            results,
            key=lambda obj: (2 if obj.finding_my_aln else 1) + (1 if obj.finding_all_aln else 0),
            reverse=bool(params.get("order_direction") == DIRECTION.descending),
        )
    elif params.get("order_by") == ORDER_BY.findings_all_aln:
        results = sorted(
            results,
            key=lambda obj: obj.finding_all_aln,
            reverse=bool(params.get("order_direction") == DIRECTION.descending),
        )
    return results

def _gather_results_for_all_alns(full_alns, agency_numbers):
    r_agency_numbers = None
    if agency_numbers:
        # Start by building a result set of just the bare agency numbers.
        # E.g. given 93 and 45, we want all of those FederalAwards
        q_agency_numbers = Q(federal_agency_prefix__in=map(lambda aln: aln.prefix, agency_numbers))
        r_agency_numbers = FederalAward.objects.filter(q_agency_numbers)

    r_full_alns = None
    if full_alns:
        # Now, build the OR for the full ALNs
        # Eg. 84.011 84.012 21.014
        q_full_alns = Q()
        for full_aln in full_alns:
            q_full_alns.add(
                Q(federal_agency_prefix=full_aln.prefix)
                & Q(federal_award_extension=full_aln.program),
                Q.OR,
            )
        if q_full_alns != Q():
            r_full_alns = FederalAward.objects.filter(q_full_alns)
    
    r_all_alns = None
    if r_agency_numbers and r_full_alns:
        # We need all of these. So, we union them.
        r_all_alns = r_agency_numbers.union(r_full_alns)
    elif r_agency_numbers:
        r_all_alns = r_agency_numbers
    elif r_full_alns:
        r_all_alns = r_full_alns
    
    return r_all_alns

def _annotate_findings(g_results, params, r_all_alns):
    # Which report ids have findings?
    finding_on_my_alns = r_all_alns.filter(findings_count__gt=0)
    q_my_alns = Q(report_id__in=Subquery(finding_on_my_alns.values_list('report_id'))) #_id_id
    annotate_on_my_alns = g_results.filter(q_my_alns)
    annotate_on_my_alns_report_ids = set(annotate_on_my_alns.values_list('report_id', flat=True))

    # Get the list of agency numbers from the ALNs
    # e.g. turn 45.012 93 21.010 into [45, 93, 21]
    all_agency_numbers = list(map(lambda a: a.prefix, _get_all_agency_numbers(params)))
    logger.info(f"_annotate_findings looking for agency numbers {all_agency_numbers}")
    # Find all of the FederalAward rows that are NOT from those agencies AND have findings gt 0
    q = Q()
    # First, make sure we are dealing with awards that have non-zero findings counts.
    q_findings_gt_0 = Q(findings_count__gt=0)
    q.add(q_findings_gt_0, Q.AND)
    # And, make sure it is NOT one of ours. That means it is one of the *agencies* that we are 
    # considering. (This is a bit broader than ALN prefix/suffix).
    # q_is_one_of_ours = Q()
    # for an in all_agency_numbers:
    #     q_is_one_of_ours.add(Q(federal_agency_prefix=an), Q.OR)
    # ^^ is much slower than the below...
    q_is_one_of_ours = Q(federal_agency_prefix__in=all_agency_numbers)
    # Here is where it is NOT one of ours.
    q.add(~q_is_one_of_ours, Q.AND)
    # Get a result set
    r = FederalAward.objects.filter(q)
    # Now, make sure that the report id in this set is one of MY report ids.
    q_my_aln_rids = Q(report_id__in=annotate_on_my_alns_report_ids) #_id_id
    q.add(q_my_aln_rids, Q.AND)
    # Fitler out everything where agency number is one of ours
    r = FederalAward.objects.filter(q)
    # This gives us a set where we know where there is a finding on an award that is one 
    # of ours, and the finding is NOT attached to one of our searched-for agencies.
    r_fa_not_in_all_agency_numbers = r.filter(q)

    # Then do a subquery to get the g_results
    q_all_alns = Q(report_id__in=Subquery(r_fa_not_in_all_agency_numbers.values_list('report_id'))) #_id_id
    annotate_on_all_alns = g_results.filter(q_all_alns)
    annotate_on_all_alns_report_ids = set(annotate_on_all_alns.values_list('report_id', flat=True))

    my_count = annotate_on_my_alns.count()
    any_count = annotate_on_all_alns.count()
    logger.info(f"_annotate_findings my[{my_count}] any[{any_count}]")
    # logger.info(f"my {annotate_on_my_alns_report_ids}")
    # logger.info(f"any {annotate_on_all_alns_report_ids}")

    only_count = 0
    both_count = 0
    for r in g_results:
        r.finding_my_aln = False
        r.finding_all_aln = False

        if r.report_id in annotate_on_my_alns_report_ids:
            r.finding_my_aln = True
            
        if r.report_id in annotate_on_all_alns_report_ids:
            r.finding_all_aln = True
        
        if r.finding_my_aln and not r.finding_all_aln:
            only_count += 1
        if r.finding_my_aln and r.finding_all_aln:
            both_count += 1

    logger.info(f"_annotate_findings only_count[{only_count}] both_count[{both_count}]")
    return g_results

# https://stackoverflow.com/questions/480214/how-do-i-remove-duplicates-from-a-list-while-preserving-order
def unique_maintaining_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

# This takes all alns and extracts a unique set of 
# the agency numbers from everything.
# e.g. 92.010 45 21.010 => [ALN(92), 45, 21]
def _get_all_agency_numbers(params):
    gan = _get_agency_numbers(params)
    gfa = _get_full_alns(params)
    combined = [ALN(x.prefix, None) for x in gan.union(gfa)]
    return set(combined)

def _get_agency_numbers(params):
    alns = params.get("alns", [])
    split_alns = set()
    for aln in alns:
        if len(aln) == 2:
            split_alns.update([ALN(aln, None)])
        else:
            pass
    return split_alns

def _get_full_alns(params):
    alns = params.get("alns", [])
    split_alns = set()
    for aln in alns:
        if len(aln) == 2:
            pass
        else:
            split_aln = aln.split(".")
            if len(split_aln) == 2:
                # The [wrapping] is so the tuple goes into the set as a tuple.
                # Otherwise, the individual elements go in unpaired.
                # split_alns.update([tuple(split_aln)])
                split_alns.update([ALN(split_aln[0], split_aln[1])])
    return split_alns
