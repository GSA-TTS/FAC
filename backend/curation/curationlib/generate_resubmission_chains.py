import logging

from curation.curationlib.audit_distance import (
    audit_equivalence_key,
    get_audit_year,
    set_distance,
)
from curation.curationlib.export_resubmission_chains import order_reports_key
from curation.curationlib.fetch_sacs import (
    fetch_disseminated_sacs_for_ay,
    fetch_disseminated_sacs_for_report_ids,
)

logger = logging.getLogger(__name__)


class MinDist:
    pass


def get_and_generate_submission_chains_by_equivalence(AY=None, noisy=False):
    sacs = fetch_disseminated_sacs_for_ay(AY=AY, noisy=noisy)
    sorted_chains = generate_submission_chains_by_equivalence(sacs, noisy=noisy)
    return sorted_chains


def get_and_generate_submission_chains_by_distance(AY=None, noisy=False):
    sacs = fetch_disseminated_sacs_for_ay(AY=AY, noisy=noisy)
    sorted_chains = generate_submission_chains_by_distance(sacs, noisy=noisy)
    return sorted_chains


def get_and_generate_submission_chain_by_report_ids(report_ids=None, noisy=False):
    return fetch_disseminated_sacs_for_report_ids(report_ids=report_ids, noisy=noisy)


def generate_submission_chains_by_equivalence(sacs, noisy=False):
    """
    Group submissions into resubmission chains using exact field equivalence.
    We feel these fields are sufficient to avoid any false attribution.

    Two submissions belong to the same chain when they share identical values for
    `auditee_uei`, `audit_year`, `ein`, `auditee_name`, and `auditee_email`.
    Submissions whose UEI is GSA_MIGRATION treat it as None. Those are matched on all the other fields instead.
    GSA_MIGRATION submissions have a "partial" key, since the UEI is missing. We put these in buckets first.
    When the non-migrated submissions are added, we try to match the "partial" part of their key with the GSA_MIGRATION submissions first.

    All chains with only one SAC are dropped. The final result is sorted by AY, but the buckets themselves are unsorted.
    """
    chains = {}
    partial_index = {}

    recent_sacs = []
    gsa_migration_sacs = []

    for r in sacs:
        r.key = audit_equivalence_key(r)
        if r.key[0] is None:
            gsa_migration_sacs.append(r)
        else:
            recent_sacs.append(r)

    # Insert non-migrated submissions first so their keys populate partial_index.
    for rndx, r in enumerate(recent_sacs):
        key = r.key  # key[0] is None
        partial = key[1:]
        if noisy:
            logger.info(
                f"[equivalence] normal {rndx}/{len(recent_sacs)}: "
                f"{r.report_id}  key={key}"
            )
        if key not in chains:
            chains[key] = []
            partial_index[partial] = key
        chains[key].append(r)

    # Now insert GSA migrated submissions, matching on the partial key.
    for rndx, r in enumerate(gsa_migration_sacs):
        key = r.key  # key[0] is None
        partial = key[1:]
        if noisy:
            logger.info(
                f"[equivalence] migration {rndx}/{len(gsa_migration_sacs)}: "
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

    # Discard chains with one lonely SAC.
    chains = [chain for chain in chains.values() if len(chain) > 1]

    # Sort all chains by AY. Chances are, this command is being run by the AY. In which case, this sort is a no-op.
    # But, it helps us see any obviously wrong submissions and it is useful when many years are run at once.
    # Then, sort each chain by submission date so the oldest comes first.
    sorted_chains = sorted(chains, key=lambda chain: get_audit_year(chain[0]))
    sorted_chains = [sorted(chain, key=order_reports_key) for chain in sorted_chains]
    return sorted_chains


def generate_submission_chains_by_distance(sacs, noisy=False):
    """
    Levenshtein distance based chaining, kept for future curation actions.

    For each submission, compute its distance to the existing chains.
    If it is below the threshold, insert it into an existing chain.
    Otherwise, insert into a new chain.
    """
    chains = []
    THRESHOLD = 3

    for rndx, r in enumerate(sacs):
        if noisy:
            print(
                f"Processing {rndx} of {len(sacs)}: {r.report_id} chains: {len(chains)}"
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

    # Discard chains with one lonely SAC.
    chains = [chain for chain in chains if len(chain) > 1]

    sorted_chains = sorted(chains, key=lambda chain: get_audit_year(chain[0]))
    sorted_chains = [sorted(chain, key=order_reports_key) for chain in sorted_chains]
    return sorted_chains
