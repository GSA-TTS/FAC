import logging

from curation.curationlib.audit_distance import (
    audit_equivalence_key,
    get_audit_year,
    set_distance,
)
from curation.curationlib.sac_disseminated_records_postgres import (
    fetch_sac_disseminated_records_postgres,
)

logger = logging.getLogger(__name__)


class MinDist:
    pass


def generate_resubmission_chains(AY=None, noisy=False):
    records = fetch_sac_disseminated_records_postgres(AY=AY, noisy=noisy)
    sorted_chains = generate_chains_from_records_by_equivalence(records, noisy=noisy)
    return sorted_chains


def generate_resubmission_chains_by_distance(AY=None, noisy=False):
    records = fetch_sac_disseminated_records_postgres(AY=AY, noisy=noisy)
    sorted_chains = generate_chains_from_records_by_distance(records, noisy=noisy)
    return sorted_chains


def generate_chains_from_records_by_equivalence(records, noisy=False):
    """
    Group records into resubmission chains using exact field equivalence.
    We feel these fields are sufficient to avoid any false attribution.

    Two records belong to the same chain when they share identical values for
    `auditee_uei`, `audit_year`, `ein`, `auditee_name`, and `auditee_email`.
    Records whose UEI is GSA_MIGRATION treat it as None. Those are matched on all the other fields instead.
    GSA_MIGRATION records have a "partial" key, since the UEI is missing. We put these in buckets first.
    When the non-migrated records are added, we try to match the "partial" part of their key with the GSA_MIGRATION records first.

    All chains with only one record are dropped. The final result is sorted by AY, but the buckets themselves are unsorted.
    """
    chains = {}
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
        if key not in chains:
            chains[key] = []
            partial_index[partial] = key
        chains[key].append(r)

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
            # Absorb into the matching GSA_MIGRATION chain.
            canonical_key = partial_index[partial]
        else:
            # No peer found - create a GSAFAC-only chain under the None key.
            canonical_key = key
            chains.setdefault(canonical_key, [])
            partial_index[partial] = canonical_key
        chains[canonical_key].append(r)

    # Discard chains with one lonely record.
    chains = [chain for chain in chains.values() if len(chain) > 1]

    # Sort by AY. Chances are, this command is being run by the AY. In which case, this sort is a no-op.
    # But, it lets us see any obviously wrong records and it is useful when many years are run at once.
    # Each chain is sorted by submission date further down the line.
    sorted_chains = sorted(chains, key=lambda chain: get_audit_year(chain[0]))
    return sorted_chains


def generate_chains_from_records_by_distance(records, noisy=False):
    """
    Levenshtein distance based chaining, kept for future curation actions.

    For each record, compute its distance to the existing chains.
    If it is below the threshold, insert it into an existing chain.
    Otherwise, insert into a new chain.
    """
    chains = []
    THRESHOLD = 3

    for rndx, r in enumerate(records):
        if noisy:
            print(
                f"Processing {rndx} of {len(records)}: {r.report_id} chains: {len(chains)}"
            )
        # Start infinitely far apart
        md = MinDist()
        md.distance = float("inf")
        md.chain_index = -1

        for ndx, chain in enumerate(chains):
            d = set_distance(r, chain)

            if d < md.distance:
                md.distance = d
                md.chain_index = ndx

        r.distance = md.distance

        if md.distance < THRESHOLD:
            r.order = len(chains[md.chain_index])
            chains[md.chain_index].append(r)
        else:
            new_chain = list()
            r.order = 0
            new_chain.append(r)
            chains.append(new_chain)

    # Discard chains with one lonely record.
    chains = [chain for chain in chains if len(chain) > 1]

    sorted_chains = sorted(chains, key=lambda chain: get_audit_year(chain[0]))
    return sorted_chains
