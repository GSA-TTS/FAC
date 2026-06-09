import csv
import json
import logging
import sys

from django.core.management.base import BaseCommand
from django.db import transaction

from audit.models import (
    SingleAuditChecklist,
    SubmissionEvent,
    User,
)
from audit.models.constants import RESUBMISSION_STATUS, STATUS
from users.models import StaffUser
from curation.curationlib.audit_distance import (
    prep_string,
    get_audit_year,
    order_reports_key,
)

logger = logging.getLogger(__name__)

# Columns that must be present in the CSV produced by link_resubmissions.
REQUIRED_COLUMNS = {"report_id", "prior_submission_status", "prior_resubmission_meta"}
UNLINKED_RESUB_STATUS = {
    "version": 0,
    "resubmission_status": RESUBMISSION_STATUS.UNKNOWN,
}


def _parse_meta(raw):
    """
    Pull the JSON resub metadata from the CSV.

    Submissions whose prior_resubmission_meta is empty were NULL before linkage.
    They must be restored to version 0 rather than NULL,
    because a NULL would be redisseminated as version 1.
    """
    if raw == "" or raw is None:
        return UNLINKED_RESUB_STATUS

    return json.loads(raw)


def _load_report_ids(report_ids):
    """
    Read the report_ids and return a list of row dicts.
    """
    ordered_sac_chain = _get_ordered_sac_chain(report_ids)
    rows = []

    for sac in ordered_sac_chain:
        rows.append(
            {
                "chain_index": 0,
                "report_id": sac.report_id,
                "audit_year": get_audit_year(sac),
                "fac_accepted_date": order_reports_key(sac).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "auditee_uei": sac.general_information["auditee_uei"],
                "auditee_ein": sac.general_information["ein"],
                "auditee_email": prep_string(sac.general_information["auditee_email"]),
                "auditee_name": prep_string(sac.general_information["auditee_name"]),
                "auditee_state": prep_string(sac.general_information["auditee_state"]),
                "prior_submission_status": STATUS.DISSEMINATED,
                "prior_resubmission_meta": (json.dumps(UNLINKED_RESUB_STATUS)),
            },
        )

    return rows


def _get_ordered_sac_chain(report_ids):
    """Returns a list of SACs ordered by version"""
    sacs_by_version = {}
    for report_id in report_ids:
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
        except SingleAuditChecklist.DoesNotExist:
            logger.error(f"SAC not found: {report_id} — exiting. ")
            sys.exit(-1)

        sacs_by_version[sac.resubmission_meta["version"]] = sac

    len_sacs = len(sacs_by_version)
    len_report_ids = len(report_ids)
    if len_sacs != len_report_ids:
        logger.error(f"Only found {len_sacs} of {len_report_ids} submissions. Exiting.")
        sys.exit(-1)

    ordered_sacs = []
    all_versions = sacs_by_version.keys()

    for v in sorted(all_versions):
        ordered_sacs.append(sacs_by_version[v])

    return ordered_sacs


def _load_csv(csv_path):
    """
    Read the prior-state CSV and return a list of row dicts. Exits early if anything is missing from the CSV.
    """
    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if not rows:
        logger.error(f"CSV is empty: {csv_path}")
        sys.exit(-1)

    missing = REQUIRED_COLUMNS - set(rows[0].keys())
    if missing:
        logger.error(
            f"CSV is missing required columns: {missing}. "
            "Ensure the CSV was produced by a current version of link_resubmissions."
        )
        sys.exit(-1)

    return rows


def _chain_creates_orphan(chain_rows):
    """Returns true if unlinking the chain's latest creates an orphan"""
    latest_report_id = chain_rows[-1]["report_id"]
    sac = SingleAuditChecklist.objects.get(report_id=latest_report_id)
    orphaned_report_id = sac.resubmission_meta.get("next_report_id", None)

    if orphaned_report_id:
        logger.error(
            f"Unlinking newest report_id given ({latest_report_id}) would orphan {orphaned_report_id} - skipping chain.",
        )
        return True

    return False


def _chain_contains_version_skip(chain_rows):
    """Returns true if the given chain contains a version skip"""
    cur_ver = last_ver = None

    for row in chain_rows:
        cur_ver = json.loads(row["prior_resubmission_meta"])["version"]

        if last_ver and last_ver - cur_ver != 1:
            logger.error(
                f"Submission chain contains a {last_ver} to {cur_ver} version skip for {row["report_id"]} - skipping chain.",
            )
            return True
        else:
            last_ver = cur_ver

    return False


def _restore_sacs(rows, user, noisy=False):
    """
    Restore submission_status and resubmission_meta for every row given.

    SACs are processed in reverse order so that a DEPRECATED submission is never
    left transiently pointing at a submission that has already been reset.
    """
    # Group rows by chain_index. They should come this way from the CSV, but just to be safe.
    chains = {}
    for row in rows:
        idx = int(row["chain_index"])
        chains.setdefault(idx, []).append(row)

    # Iterate chains in descending order. Within each chain, move in reverse order.
    for chain_index in sorted(chains.keys(), reverse=True):
        chain_rows = chains[chain_index]

        if _chain_creates_orphan(chain_rows):
            continue

        if _chain_contains_version_skip(chain_rows):
            continue

        r_chain_rows = reversed(chains[chain_index])
        for row in r_chain_rows:
            report_id = row["report_id"]
            prior_status = row["prior_submission_status"]

            try:
                prior_meta = _parse_meta(row["prior_resubmission_meta"])
            except json.JSONDecodeError:
                logger.error(
                    f"Invalid JSON in prior_resubmission_meta for SAC: {report_id} — skipping submission."
                )
                continue

            try:
                sac = SingleAuditChecklist.objects.get(report_id=report_id)
            except SingleAuditChecklist.DoesNotExist:
                logger.error(f"SAC not found: {report_id} — skipping submission. ")
                continue

            if noisy:
                logger.info(
                    f"Restoring {report_id}: "
                    f"status {sac.submission_status!r} -> {prior_status!r}, "
                    f"meta {sac.resubmission_meta} -> {prior_meta}"
                )

            # Finally set the data, and propagate it to the dissemination tables.
            sac.submission_status = prior_status
            sac.resubmission_meta = prior_meta

            with transaction.atomic():
                sac.save(
                    administrative_override=True,
                    event_user=user,
                    event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_RESUBMISSION_UNDO,
                )
                sac.redisseminate()


def _comma_separated_list(string):
    return string.split(",")


class Command(BaseCommand):
    """
    Undo a prior run of link_resubmissions by restoring pre-linkage metadata.

    Reads the CSV produced by link_resubmissions and writes those values back, then redisseminates each submission.
    Alternatively, a list of report_ids can be provided.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            required=False,
            help="Path to the CSV file produced by a prior run of link_resubmissions",
        )
        parser.add_argument(
            "--report_ids",
            type=_comma_separated_list,
            required=False,
            help="Report IDs to process",
        )
        parser.add_argument(
            "--email",
            type=str,
            required=True,
            help="The email of the FAC staff making this change",
        )
        parser.add_argument("--noisy", action="store_true")
        parser.add_argument("--quiet", dest="noisy", action="store_false")
        parser.set_defaults(noisy=False)

    def handle(self, *args, **options):
        csv = options["csv"]
        report_ids = options["report_ids"]
        noisy = options["noisy"]
        email = options["email"]

        # Verify staff user. Note that it's VERY hard to get here without already being staff.
        try:
            ok_staff_user = StaffUser.objects.get(staff_email=email)
        except StaffUser.DoesNotExist:
            logger.error(f"Staff user {email} does not exist")
            ok_staff_user = False
        if not ok_staff_user:
            sys.exit(-1)

        if csv and report_ids:
            logger.error("Only one of --csv and --report_ids must be provided.")
            sys.exit(-1)
        if report_ids:
            rows = _load_report_ids(report_ids)
        elif csv:
            rows = _load_csv(csv)
            report_ids = [r["report_id"] for r in rows]

        len_report_ids = len(report_ids)
        if len_report_ids == 0:
            logger.info("Exiting.")
            sys.exit(0)
        else:
            logger.info(f"Unlinking {len_report_ids} submissions.")

        if noisy:
            for rid in report_ids:
                logger.info(f"  {rid}")

        k = input("\nPress `c` to continue: ")
        if k != "c":
            logger.error("Exiting.")
            sys.exit()

        # Do the thing!
        ok_user = User.objects.get(email=email)
        _restore_sacs(rows, ok_user, noisy=noisy)

        logger.info(
            f"\nUndo complete. {len(rows)} submissions restored and redisseminated."
        )
