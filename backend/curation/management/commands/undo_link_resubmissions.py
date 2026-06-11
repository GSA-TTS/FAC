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
from curation.curationlib.audit_distance import (
    prep_string,
    get_audit_year,
    order_reports_key,
)
from curation.curationlib.util import (
    exit_if_not_staff_user,
)

logger = logging.getLogger(__name__)

# Columns that must be present in the CSV produced by link_resubmissions.
REQUIRED_COLUMNS = {"report_id", "prior_submission_status", "prior_resubmission_meta"}
UNLINKED_RESUB_STATUS = {
    "version": 0,
    "resubmission_status": RESUBMISSION_STATUS.UNKNOWN,
}


def _parse_meta(row):
    """
    Pull the JSON resub metadata from the row.

    Submissions whose prior_resubmission_meta is empty were NULL before linkage.
    They must be restored to version 0 rather than NULL,
    because a NULL would be redisseminated as version 1.
    """
    raw = row["prior_resubmission_meta"]
    if raw == "" or raw is None:
        return UNLINKED_RESUB_STATUS

    try:
        return None, json.loads(raw)
    except json.JSONDecodeError as err:
        logger.error(
            f"Invalid JSON in prior_resubmission_meta for SAC: {row["report_id"]} — skipping submission."
        )
        return err, None


def _safe_sac_getter(report_id):
    """
    Returns the SAC object for the given report_id. Logs and returns an error
    upon failure.
    """
    try:
        return None, SingleAuditChecklist.objects.get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist as err:
        logger.error(f"SAC not found: {report_id} — skipping submission.")
        return err, None


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
                "resubmission_meta": sac.resubmission_meta,
                "prior_submission_status": STATUS.DISSEMINATED,
                "prior_resubmission_meta": (json.dumps(UNLINKED_RESUB_STATUS)),
            },
        )

    return rows


def _get_ordered_sac_chain(report_ids):
    """Returns a list of SACs ordered by version"""
    sacs_by_version = {}
    missing_sacs = []

    for report_id in report_ids:
        err, sac = _safe_sac_getter(report_id)
        if err:
            missing_sacs.append(report_id)
        else:
            v = sac.resubmission_meta["version"]
            sacs_by_version[v] = sac

    if missing_sacs:
        len_sacs = len(sacs_by_version)
        len_report_ids = len(report_ids)

        raise RuntimeError(
            f"Only found {len_sacs} of {len_report_ids} submissions. Missing {missing_sacs}.",
        )

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
    """Returns true if unlinking the chain would create an orphan."""
    total_rows = len(chain_rows)

    for i, row in enumerate(chain_rows):
        rid = row["report_id"]
        resubmission_meta = row["resubmission_meta"]
        prev_rid = resubmission_meta.get("previous_report_id")
        next_rid = resubmission_meta.get("next_report_id")
        is_first = i == 0
        is_last = i == total_rows - 1

        # Validate next/previous_report_ids only exist where they should be
        if is_first and prev_rid:
            logger.error(f"Submission {rid} is first but has previous_report_id {prev_rid}.")
            return True
        if not is_first and not prev_rid:
            logger.error(f"Submission {rid} isn't first but has no previous_report_id.")
            return True
        if is_last and next_rid:
            logger.error(f"Submission {rid} is last but has next_report_id {next_rid}.")
            return True
        if not is_last and not next_rid:
            logger.error(f"Submission {rid} isn't last but has no next_report_id.")
            return True

        # Validate next/previous_report_ids match what's in the chain
        if not is_first:
            prev_chain_rid = chain_rows[i - 1]["report_id"]
            expected_current_rid = chain_rows[i - 1]["resubmission_meta"].get("next_report_id")

            if prev_rid != prev_chain_rid:
                logger.error(f"Submission {rid} prev_id {prev_rid} doesn't match expected {prev_chain_rid}.")
                return True
            if rid != expected_current_rid:
                logger.error(f"Submission {prev_chain_rid} next_id {expected_current_rid} doesn't match {rid}.")
                return True

    return False


def _unlink_sacs(rows, user, noisy=False):
    """
    Unlink submission_status and resubmission_meta for every row given.

    SACs are processed in reverse order so that a DEPRECATED submission is never
    left transiently pointing at a submission that has already been unlinked.
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

        for row in reversed(chain_rows):
            report_id = row["report_id"]
            prior_status = row["prior_submission_status"]

            err, prior_meta = _parse_meta(row)
            if err:
                continue

            err, sac = _safe_sac_getter(report_id)
            if err:
                continue

            if noisy:
                logger.info(
                    f"Unlinking {report_id}: "
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

    Reads the CSV produced by link_resubmissions and writes those values back,
    then redisseminates each submission. Alternatively, a list of report_ids
    can be provided. ALL report_ids within a chain must be provided; chains
    CANNOT be partially unlinked.
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

        exit_if_not_staff_user(email)

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
        _unlink_sacs(rows, ok_user, noisy=noisy)

        logger.info(
            f"\nUndo complete. {len(rows)} submissions unlinked and redisseminated."
        )
