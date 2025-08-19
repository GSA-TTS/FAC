from curation.curationlib.audit_distance import set_distance, get_audit_year

from curation.curationlib.sac_resubmission_records_postgres import (
    fetch_sac_resubmission_records_postgres,
)

import logging

logger = logging.getLogger(__name__)


class MinDist:
    pass


def generate_resbmission_clusters(AY=None, noisy=False):
    records = fetch_sac_resubmission_records_postgres(AY=AY, noisy=noisy)
    sorted_sets = generate_clusters_from_records(records, noisy=noisy)
    return sorted_sets


def generate_clusters_from_records(records, noisy=False):
    # For each record, compute its distance to the existing sets.
    # If it is below the threshold, insert it into an existing set.
    # Otherwise, insert into a new set.
    sets = []
    THRESHOLD = 3

    for rndx, r in enumerate(records):
        if noisy:
            print(
                f"Processing {rndx} of {len(records)}: {r.report_id} sets: {len(sets)}"
            )
        # Start infinitely far apart
        md = MinDist()
        md.distance = float("inf")
        md.set_index = -1

        for ndx, s in enumerate(sets):
            d = set_distance(r, s)

            if d < md.distance:
                md.distance = d
                md.set_index = ndx

        r.distance = md.distance

        if md.distance < THRESHOLD:
            # print(f"Adding {r} to {md.set_index}")
            r.order = len(sets[md.set_index])
            sets[md.set_index].append(r)
        else:
            # print(f"Adding {r} to new set ({r.__hash__()})")
            new_s = list()
            r.order = 0
            new_s.append(r)
            sets.append(new_s)

    sorted_sets = sorted(sets, key=lambda s: get_audit_year(s[0]))
    return sorted_sets
