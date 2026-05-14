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
from users.models import StaffUser

logger = logging.getLogger(__name__)

# Columns that must be present in the CSV produced by link_resubmissions.
REQUIRED_COLUMNS = {"report_id", "prior_submission_status", "prior_resubmission_meta"}


def _parse_meta(raw):
    """
    Pull the JSON resub metadata from the CSV.

    Records whose prior_resubmission_meta is empty were NULL before linkage.
    They must be restored to version 0 rather than NULL,
    because a NULL would be redisseminated as version 1.
    """
    if raw == "" or raw is None:
        return {
            "version": 0,
            "resubmission_status": "no_resubmission_data",
        }
    return json.loads(raw)


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


def _restore_records(rows, user, noisy=False):
    """
    Restore submission_status and resubmission_meta for every row in the CSV.

    Records are processed in reverse order so that a DEPRECATED record is never
    left transiently pointing at a record that has already been reset.
    """
    # Group rows by chain_index. They should come this way from the CSV, but just to be safe.
    chains = {}
    for row in rows:
        idx = int(row["chain_index"])
        chains.setdefault(idx, []).append(row)

    # Iterate chains in descending order. Within each chain, move in reverse order.
    for chain_index in sorted(chains.keys(), reverse=True):
        chain_rows = list(reversed(chains[chain_index]))
        for row in chain_rows:
            report_id = row["report_id"]
            prior_status = row["prior_submission_status"]
            prior_meta = _parse_meta(row["prior_resubmission_meta"])

            try:
                sac = SingleAuditChecklist.objects.get(report_id=report_id)
            except SingleAuditChecklist.DoesNotExist:
                logger.error(
                    f"Record not found: {report_id} — skipping. "
                    "The database may have changed since this CSV was produced."
                )
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


class Command(BaseCommand):
    """
    Undo a prior run of link_resubmissions by restoring pre-linkage metadata.

    Reads the CSV produced by link_resubmissions and writes those values back, then redisseminates each record.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            required=True,
            help="Path to the CSV file produced by a prior run of link_resubmissions",
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
        # Verify staff user. Note that it's VERY hard to get here without already being staff.
        try:
            ok_staff_user = StaffUser.objects.get(staff_email=options["email"])
        except StaffUser.DoesNotExist:
            logger.error(f'Staff user {options["email"]} does not exist')
            ok_staff_user = False
        if not ok_staff_user:
            sys.exit(-1)

        rows = _load_csv(options["csv"])

        # Display a little summary of what will be undone before touching any records.
        report_ids = [r["report_id"] for r in rows]
        logger.info(f"CSV contains {len(rows)} records.")
        if options["noisy"]:
            for rid in report_ids:
                logger.info(f"  {rid}")

        k = input("\nPress `c` to continue...")
        if k != "c":
            logger.error("Exiting.")
            sys.exit()

        # Do the thing!
        ok_user = User.objects.get(email=options["email"])
        _restore_records(rows, ok_user, noisy=options["noisy"])

        logger.info(
            f"\nUndo complete. {len(rows)} records restored and redisseminated."
        )
