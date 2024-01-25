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
from pprint import pprint

import logging

logger = logging.getLogger(__name__)

ALN = NT("ALN", "prefix, program")

def search_alns(results, params):
    t0 = time.time()
    full_alns = _get_full_alns(params)
    agency_numbers = _get_agency_numbers(params)

    logger.info(f"full_alns {full_alns}")
    logger.info(f"agency_numbers {agency_numbers}")

    if not (full_alns or agency_numbers):
        return results
    else:
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


        all_alns_count = r_all_alns.count()
        logger.info(f"search_alns matching FederalAward rows[{all_alns_count}]")
        results = results.filter(report_id__in=Subquery(r_all_alns.values_list('report_id_id')))
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
            key=lambda obj: obj.finding_my_aln,
            reverse=bool(params.get("order_direction") == DIRECTION.descending),
        )
    elif params.get("order_by") == ORDER_BY.findings_all_aln:
        results = sorted(
            results,
            key=lambda obj: obj.finding_all_aln,
            reverse=bool(params.get("order_direction") == DIRECTION.descending),
        )
    return results

def _annotate_findings(g_results, params, r_all_alns):
    # Which report ids have findings?
    finding_on_my_alns = r_all_alns.filter(findings_count__gt=0)
    q_my_alns = Q(report_id__in=Subquery(finding_on_my_alns.values_list('report_id_id')))
    annotate_on_my_alns = g_results.filter(q_my_alns)
    annotate_on_my_alns_report_ids = set(annotate_on_my_alns.values_list('report_id', flat=True))

    # Get the list of agency numbers from the ALNs
    # e.g. turn 45.012 93 21.010 into [45, 93, 21]
    all_agency_numbers = _get_all_agency_numbers(params)
    logger.info(f"_annotate_findings looking for agency numbers {all_agency_numbers}")
    # Find all of the FederalAward rows that are NOT from those agencies AND have findings gt 0
    q_is_one_of_ours = Q()
    for an in all_agency_numbers:
        q_is_one_of_ours.add(Q(federal_agency_prefix=an), Q.OR)
        
    q_findings_gt_0 = Q(findings_count__gt=0)
    r_fa_all_gt_0 = FederalAward.objects.filter(q_findings_gt_0)
    # Fitler out everything where agency number is one of ours
    r_fa_not_in_all_agency_numbers = r_fa_all_gt_0.filter(~q_is_one_of_ours)

    # Then do a subquery to get the g_results
    q_all_alns = Q(report_id__in=Subquery(r_fa_not_in_all_agency_numbers.values_list('report_id_id')))
    annotate_on_all_alns = g_results.filter(q_all_alns)
    annotate_on_all_alns_report_ids = set(annotate_on_all_alns.values_list('report_id', flat=True))

    # fama_report_ids = finding_on_my_alns.values_list('report_id_id', flat=True)
    my_count = annotate_on_my_alns.count()
    any_count = annotate_on_all_alns.count()
    logger.info(f"_annotate_findings my[{my_count}] any[{any_count}]")
    logger.info(f"my {annotate_on_my_alns_report_ids}")
    logger.info(f"any {annotate_on_all_alns_report_ids}")
    time.sleep(3)

    for ndx, r in enumerate(g_results):
        r.finding_my_aln = False
        r.finding_all_aln = False

        if r.report_id in annotate_on_my_alns_report_ids:
            r.finding_my_aln = True
            
        if r.report_id in annotate_on_all_alns_report_ids:
            r.finding_all_aln = True

        if r.finding_my_aln and not r.finding_all_aln:
            logger.info("_annotate_findings ONLY MY ALN")
            print(f"=================== {ndx} ===================")
            for f in FederalAward.objects.filter(report_id_id=r.report_id).values("federal_agency_prefix", "federal_award_extension", "report_id_id"):
                pprint(f)
    return g_results

# https://stackoverflow.com/questions/480214/how-do-i-remove-duplicates-from-a-list-while-preserving-order
def unique_maintaining_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

# This takes all alns and extracts a unique set of 
# the agency numbers from everything.
# e.g. 92.010 45 21.010 => [92, 45, 21]
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

