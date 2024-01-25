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

logger = logging.getLogger(__name__)

ALN = NT("ALN", "prefix, program")

def search_alns(general_results, params):
    t0 = time.time()
    full_alns = _get_full_alns(params)
    agency_numbers = _get_agency_numbers(params)

    if not (full_alns or agency_numbers):
        return general_results
    else:
        r_FAs_matching_alns = _gather_results_for_all_alns(full_alns, agency_numbers)
        all_alns_count = r_FAs_matching_alns.count()
        logger.info(f"search_alns matching FederalAward rows[{all_alns_count}]")
        r_general_rids_matching_FA_rids = general_results.filter(report_id__in=Subquery(r_FAs_matching_alns.values_list('report_id'))) #_id_id
        logger.info(f"search_alns general rows[{r_general_rids_matching_FA_rids.count()}]")
        annotated = _annotate_findings(r_general_rids_matching_FA_rids, params, r_FAs_matching_alns)
        sorted = _findings_sort(annotated, params)

        t1 = time.time()
        report_timing("search_alns", params, t0, t1)
        return sorted

def _findings_sort(results, params):
    if params.get("order_by") == ORDER_BY.findings_my_aln:
        results = sorted(
            results,
            key=lambda obj: (2 if obj.finding_my_aln else 0) + (1 if obj.finding_all_aln else 0),
            reverse=bool(params.get("order_direction") == DIRECTION.descending),
        )
    elif params.get("order_by") == ORDER_BY.findings_all_aln:
        results = sorted(
            results,
            key=lambda obj: (1 if obj.finding_my_aln else 0) + (2 if obj.finding_all_aln else 0),
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

def _annotate_findings(r_generals, params, r_FA_all_alns):
    # Get the list of agency numbers from the ALNs the user searched for.
    # e.g. turn 45.012 93 21.010 into [45, 93, 21]
    agency_numbers_user_searched_for = list(map(lambda a: a.prefix, _get_all_agency_numbers(params)))
    
    ### 
    # 1. I want a set of General.report_ids that match
    #    my General query, and match the ALNs that were searched for.
    # g_results already matches my general query.
    # Now, reduce that to just report_ids where there are associated FAs
    # that do have findings on my ALNs.
    # We want FAs that are in the set of report_ids found from the general query.
    # q_my_alns = Q(report_id__in=Subquery(finding_on_my_alns.values_list('report_id'))) #_id_id

    q_in_general = Q(report_id__in=Subquery(r_generals.values_list('report_id')))
    # We have to work with FAs related to the user's query
    q_FA_the_user_searched_for = Q(federal_agency_prefix__in=agency_numbers_user_searched_for)
    q = Q()
    q.add(q_in_general, Q.AND)
    q.add(q_FA_the_user_searched_for, Q.AND)
    r_FA_in_our_interest_set = FederalAward.objects.filter(q)
    report_ids_of_interest = r_FA_in_our_interest_set.values_list('report_id', flat=True) 
    
    # logger.info("========================================")
    # logger.info(f"Report IDs of interest: {len(report_ids_of_interest)}")
    # logger.info(f"Looking for agency numbers {agency_numbers_user_searched_for}")
    # logger.info(f"RIDs of interest: {report_ids_of_interest}")
    # logger.info("========================================")

    ############################################################
    # Findings other ALNs
    ###
    # The rids of interest:
    #   * They are in our General set.
    #   * They have FAs with agency prefixes the user searched for

    # Now, I want a list of report IDs where:
    #   there are no findings for the ALNs of interest
    #   there are findings anywhere else.
    q = Q()
    q_must_be_of_interest = Q(report_id__in=Subquery(report_ids_of_interest))
    # Now, there must be findings.
    q_has_findings = Q(findings_count__gt=0)
    q.add(q_must_be_of_interest, Q.AND)
    q.add(q_has_findings, Q.AND)
    interim = FederalAward.objects.filter(q)
    # logger.info(f"interim[{interim.count()}]: {interim.values_list('report_id', flat=True)}")
    # It is not an agency the user looked for
    q_agency_sought = Q(federal_agency_prefix__in=agency_numbers_user_searched_for)
    r_other_alns = interim.exclude(q_agency_sought)
    # We want to know which report_ids are N/Y, meaning
    # the had findings, but not on an agency the user searched for.
    report_ids_excluding_user_agencies = r_other_alns.values_list("report_id", flat=True)
    # logger.info(f"report_ids excluding user search [{report_ids_excluding_user_agencies.count()}]")

    ############################################################
    # Findings my ALNs
    r_my_alns = interim.filter(q_agency_sought)
    report_ids_including_user_agencies = r_my_alns.values_list("report_id", flat=True)
    # logger.info(f"report_ids excluding user search [{report_ids_including_user_agencies.count()}]")


    only_count = 0
    both_count = 0
    for r in r_generals:
        r.finding_my_aln = False
        r.finding_all_aln = False

        if r.report_id in report_ids_including_user_agencies:
            r.finding_my_aln = True
            
        if r.report_id in report_ids_excluding_user_agencies:
            r.finding_all_aln = True
        
        if r.finding_my_aln and not r.finding_all_aln:
            only_count += 1
        if r.finding_my_aln and r.finding_all_aln:
            both_count += 1

    # logger.info(f"_annotate_findings only_count[{only_count}] both_count[{both_count}]")
    return r_generals

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

