from django.db.models import Q, Subquery
from collections import namedtuple as NT
from dissemination.models import FederalAward
import time
from .search_general import report_timing

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

    awards_filters = _build_aln_q(full_alns, agency_numbers)
    filtered_general_results = general_results.filter(awards_filters).distinct()

    # After migrating in historical data, this feature uses too much RAM/CPU.
    # Disabled until we rework the expensive queries.
    # annotated = _annotate_findings(
    #     r_general_rids_matching_FA_rids, params, r_FAs_matching_alns
    # )
    # sorted = _findings_sort(annotated, params)
    # return sorted

    t1 = time.time()
    report_timing("search_alns", params, t0, t1)
    return filtered_general_results


def _findings_sort(results, params):
    if params.get("order_by") == ORDER_BY.findings_my_aln:
        results = sorted(
            results,
            key=lambda obj: (2 if obj.finding_my_aln else 0)
            + (1 if obj.finding_all_aln else 0),
            reverse=bool(params.get("order_direction") == DIRECTION.descending),
        )
    elif params.get("order_by") == ORDER_BY.findings_all_aln:
        results = sorted(
            results,
            key=lambda obj: (1 if obj.finding_my_aln else 0)
            + (2 if obj.finding_all_aln else 0),
            reverse=bool(params.get("order_direction") == DIRECTION.descending),
        )
    return results


def _build_aln_q(full_alns, agency_numbers):
    """Build a filter for the agency numbers and full ALNs."""
    q = Q()
    if agency_numbers:
        # Build a filter for the agency numbers. E.g. given 93 and 45
        q |= Q(federal_agency_prefix__in=[an.prefix for an in agency_numbers])

    if full_alns:
        for full_aln in full_alns:
            q |= Q(federal_agency_prefix=full_aln.prefix) & Q(
                federal_award_extension=full_aln.program
            )

    return q


def _gather_results_for_all_alns(full_alns, agency_numbers):
    r_agency_numbers = None
    if agency_numbers:
        # Start by building a result set of just the bare agency numbers.
        # E.g. given 93 and 45, we want all of those FederalAwards
        q_agency_numbers = Q(
            federal_agency_prefix__in=map(lambda aln: aln.prefix, agency_numbers)
        )
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

    r_all_alns = FederalAward.objects.none()
    if r_agency_numbers and r_full_alns:
        # We need all of these. So, we union them.
        r_all_alns = r_agency_numbers | r_full_alns
    elif r_agency_numbers:
        r_all_alns = r_agency_numbers
    elif r_full_alns:
        r_all_alns = r_full_alns

    return r_all_alns


def _annotate_findings(g_results, params, r_all_alns):
    # ----- The General objects that will recieve 'Y' for finding_my_aln -----
    r_fa_findings_on_my_alns = r_all_alns.filter(findings_count__gt=0)
    q_my_alns = Q(
        report_id__in=Subquery(r_fa_findings_on_my_alns.values_list("report_id"))
    )
    annotate_on_my_alns = g_results.filter(q_my_alns)
    annotate_on_my_alns_report_ids = set(
        annotate_on_my_alns.values_list("report_id", flat=True)
    )

    # ----- The General objects that will recieve 'Y' for finding_all_aln -----
    all_agency_numbers = list(map(lambda a: a.prefix, _get_all_agency_numbers(params)))
    logger.info(f"Looking for agency numbers {all_agency_numbers}")
    r_all_related_awards_report_ids = set(g_results.values_list("report_id", flat=True))
    q = Q()
    # Q (query): All FederalAward's with findings
    q.add(Q(findings_count__gt=0), Q.AND)
    # Q: All FederalAward's with findings under our ALNs
    q_is_one_of_ours = Q(federal_agency_prefix__in=all_agency_numbers)
    # Q: All FederalAward's with findings that are NOT under our ALNs
    q.add(~q_is_one_of_ours, Q.AND)
    # Q: All FederalAward's with findings that are NOT under our ALNs, but are related to one of our general results
    q_my_aln_rids = Q(report_id__in=r_all_related_awards_report_ids)
    q.add(q_my_aln_rids, Q.AND)
    # R (results): Execute on Q
    r_fa_not_in_all_agency_numbers = FederalAward.objects.filter(q)
    # Q: Utilize a subquery to get the General objects that match up with the above results
    q_all_alns = Q(
        report_id__in=Subquery(r_fa_not_in_all_agency_numbers.values_list("report_id"))
    )
    annotate_on_all_alns = g_results.filter(q_all_alns)
    annotate_on_all_alns_report_ids = set(
        annotate_on_all_alns.values_list("report_id", flat=True)
    )

    # ----- Annotate the General objects with our Y/N fields -----
    my_count = 0
    any_count = 0
    only_my_count = 0
    only_other_count = 0
    both_count = 0
    for r in g_results:
        r.finding_my_aln = False
        r.finding_all_aln = False

        if r.report_id in annotate_on_my_alns_report_ids:
            r.finding_my_aln = True
            my_count += 1

        if r.report_id in annotate_on_all_alns_report_ids:
            r.finding_all_aln = True
            any_count += 1

        if r.finding_my_aln and not r.finding_all_aln:
            only_my_count += 1
        if not r.finding_my_aln and r.finding_all_aln:
            only_other_count += 1
        if r.finding_my_aln and r.finding_all_aln:
            both_count += 1
    logger.info(
        f"_annotate_findings my[{my_count}] other[{any_count}] \nonly_my_count[{only_my_count}] only_other_count[{only_other_count} ]\nboth_count[{both_count}]"
    )

    return g_results


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
