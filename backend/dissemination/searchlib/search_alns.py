from django.db.models import Q
from collections import namedtuple as NT

import logging

logger = logging.getLogger(__name__)

ALN = NT("ALN", "prefix, program")


def audit_search_alns(params):
    full_alns = _get_full_alns(params)
    agency_numbers = _get_agency_numbers(params)

    if not (full_alns or agency_numbers):
        return Q()

    query = Q()
    if agency_numbers:
        # Build a filter for the agency numbers. E.g. given 93 and 45
        for agency_number in agency_numbers:
            query |= Q(agency_prefixes__icontains=agency_number.prefix)

    if full_alns:
        for full_aln in full_alns:
            query |= Q(agency_prefixes__icontains=full_aln.prefix) & Q(
                agency_extensions__icontains=full_aln.program
            )

    return query


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
