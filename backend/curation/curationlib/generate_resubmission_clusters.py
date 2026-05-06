import logging

from curation.curationlib.audit_distance import (
    audit_equivalence_key,
    get_audit_year,
    set_distance,
)
from curation.curationlib.sac_resubmission_records_postgres import (
    fetch_sac_resubmission_records_postgres,
)

logger = logging.getLogger(__name__)


class MinDist:
    pass


def generate_resbmission_clusters(AY=None, noisy=False):
    records = fetch_sac_resubmission_records_postgres(AY=AY, noisy=noisy)
    sorted_sets = generate_clusters_from_records_by_equivalence(records, noisy=noisy)
    return sorted_sets


def generate_clusters_from_records_by_equivalence(records, noisy=False):
    """
    Group records into resubmission clusters using exact field equivalence.
    We feel these fields are sufficient to avoid any false attribution.

    Two records belong to the same cluster when they share identical values
    for `auditee_uei`, `audit_year`, `ein`, `auditee_name`, and `auditee_email`.
    Records whose UEI is GSA_MIGRATION treat it as None. Those are matched on all the other fields instead.
    GSA_MIGRATION records have a "partial" key, since the UEI is missing. We put these in buckets first.
    When the non-migrated records are added, we try to match the "partial" part of their key with the GSA_MIGRATION records first.

    All buckets with only one record are dropped. The final result is sorted by AY, but the buckets themselves are unsorted.
    """
    buckets = {}
    partial_index = {}

    recent_records = []
    gsa_migration_records = []

    for r in records:
        r.key = audit_equivalence_key(r)
        if r.key[0] is None:
            gsa_migration_records.append(r)
        else:
            recent_records.append(r)

    # Insert non-migrated records first so their keys populate partial_index.
    for rndx, r in enumerate(recent_records):
        key = r.key  # key[0] is None
        partial = key[1:]
        if noisy:
            logger.info(
                f"[equivalence] normal {rndx}/{len(recent_records)}: "
                f"{r.report_id}  key={key}"
            )
        if key not in buckets:
            buckets[key] = []
            partial_index[partial] = key
        buckets[key].append(r)

    # Now insert GSA migrated records, matching on the partial key.
    for rndx, r in enumerate(gsa_migration_records):
        key = r.key  # key[0] is None
        partial = key[1:]
        if noisy:
            logger.info(
                f"[equivalence] migration {rndx}/{len(gsa_migration_records)}: "
                f"{r.report_id}  partial={partial}"
            )
        if partial in partial_index:
            # Absorb into the matching GSA_MIGRATION bucket.
            canonical_key = partial_index[partial]
        else:
            # No peer found - create a GSAFAC-only bucket under the None key.
            canonical_key = key
            buckets.setdefault(canonical_key, [])
            partial_index[partial] = canonical_key
        buckets[canonical_key].append(r)

    # Discard buckets with one lonely record - no link is necessary.
    clusters = [bucket for bucket in buckets.values() if len(bucket) > 1]

    # Sort by AY. Chances are, this command is being run by the AY. In which case, this sort is a no-op.
    # But, it lets us see any obviously wrong records and it is useful when many years are run at once.
    # Each bucket is sorted by submission date further down the line.
    sorted_sets = sorted(clusters, key=lambda s: get_audit_year(s[0]))
    return sorted_sets


def generate_clusters_from_records_by_distance(records, noisy=False):
    """
    Levenshtein distance based clustering, kept for future curation actions.

    For each record, compute its distance to the existing sets.
    If it is below the threshold, insert it into an existing set.
    Otherwise, insert into a new set.
    """
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
            r.order = len(sets[md.set_index])
            sets[md.set_index].append(r)
        else:
            new_s = list()
            r.order = 0
            new_s.append(r)
            sets.append(new_s)

    sorted_sets = sorted(sets, key=lambda s: get_audit_year(s[0]))
    return sorted_sets
