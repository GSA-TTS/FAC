import logging
import sys

from django.db import transaction
from django.core.management.base import BaseCommand

from audit.models import (
    SingleAuditChecklist,
    SubmissionEvent,
    User,
)
from audit.models.constants import RESUBMISSION_STATUS
from users.models import StaffUser
from audit.models.constants import STATUS
from curation.curationlib.generate_resubmission_chains import (
    get_and_generate_submission_chains_by_equivalence,
)
from curation.curationlib.export_resubmission_chains import (
    export_chains_as_csv,
    export_chains_as_markdown,
)

logger = logging.getLogger(__name__)


def lfilter(fun, ls):
    return list(filter(fun, ls))


def point_old_to_new(
    first: SingleAuditChecklist, second: SingleAuditChecklist, u: User
):
    # Points the first at the second, where the first
    # is the older of the two audits.

    # If the first has no resubmission metadata, it must be the first in a chain.
    # If it is of version 0 it must also be first in the chain.
    # This is like calling 'initiate_resubmission' on an audit.
    if first.resubmission_meta is None or first.resubmission_meta.get("version") == 0:
        logger.info(f"First in chain: {first.report_id} -> {second.report_id}")
        first.resubmission_meta = {
            "version": 1,
            "next_row_id": second.id,
            "next_report_id": second.report_id,
            "resubmission_status": RESUBMISSION_STATUS.DEPRECATED,
        }
        first.submission_status = STATUS.RESUBMITTED
        second.resubmission_meta = {
            "version": 2,
            "previous_row_id": first.id,
            "previous_report_id": first.report_id,
            "resubmission_status": RESUBMISSION_STATUS.MOST_RECENT,
        }
        second.submission_status = STATUS.DISSEMINATED

        # Now save them.
        with transaction.atomic():
            first.save(
                administrative_override=True,
                event_user=u,
                event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_RESUBMISSION_LINKAGE,
            )
            second.save(
                administrative_override=True,
                event_user=u,
                event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_RESUBMISSION_LINKAGE,
            )
            # Once we modify the SAC records, we need to redisseminate
            first.redisseminate()
            second.redisseminate()

    # If the first one has metadata, that means we're linking things
    # that are part of a chain.
    elif first.resubmission_meta is not None:
        logger.info(f"Middle of chain: {first.report_id} -> {second.report_id}")
        # Extend the metadata of the first report with information about
        # it's next. It probably had a previous_, but no next.
        # We also want to deprecate it, because it is no longer the most_recent.
        first.resubmission_meta = first.resubmission_meta | {
            "next_row_id": second.id,
            "next_report_id": second.report_id,
            "resubmission_status": RESUBMISSION_STATUS.DEPRECATED,
        }
        first.submission_status = STATUS.RESUBMITTED
        # The second is new to the chain, so we just provide the previous.
        # The version number is one more than the previous
        second.resubmission_meta = {
            "version": first.resubmission_meta["version"] + 1,
            "previous_row_id": first.id,
            "previous_report_id": first.report_id,
            "resubmission_status": RESUBMISSION_STATUS.MOST_RECENT,
        }
        second.submission_status = STATUS.DISSEMINATED
        with transaction.atomic():
            first.save(
                administrative_override=True,
                event_user=u,
                event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_RESUBMISSION_LINKAGE,
            )
            second.save(
                administrative_override=True,
                event_user=u,
                event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_RESUBMISSION_LINKAGE,
            )
            # And, redisseminate.
            first.redisseminate()
            second.redisseminate()
    else:
        logger.error("This is an impossible linking condition.")
        logger.error(f"first: {first}")
        logger.error(f"second: {second}")
        sys.exit(-1)


def annotate_old(options):
    # Now, everything in that audit year that has no metadata is
    # an unknown to us. We should annotate it. This way, all audits in that
    # year have resubmission metadata. We won't do anything to in-flight audits.
    # They will get annotated when they are saved.
    u = User.objects.get(email=options["email"])
    for sac in SingleAuditChecklist.objects.filter(
        resubmission_meta__isnull=True,
        submission_status="disseminated",
        general_information__auditee_fiscal_period_end__startswith=options[
            "audit_year"
        ],
    ):
        sac.resubmission_meta = {
            "version": 0,
            "resubmission_status": "no_resubmission_data",
        }
        sac.save(
            administrative_override=True,
            event_user=u,
            event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_RESUBMISSION_ANNOTATION,
        )
        sac.redisseminate()


def annotate_linked_reports(options, sorted_chains):
    u = User.objects.get(email=options["email"])
    for linked in sorted_chains:
        # Chains arrive sorted by submission date, oldest first.
        the_length = len(linked)
        # range() is from [0, length) (inclusive, exclusive)
        for ndx in range(the_length - 1):
            # I want to link this to next, and visa-versa.
            this_ndx = ndx
            next_ndx = ndx + 1
            # Are they both less than the length? If so, they can be linked.
            if this_ndx < the_length and next_ndx <= the_length:
                try:
                    this_sac = linked[this_ndx]
                    next_sac = linked[next_ndx]
                    point_old_to_new(this_sac, next_sac, u)
                except IndexError:
                    # Should not get here.
                    logger.error(
                        f"length: {the_length} first: {this_ndx} second: {next_ndx}"
                    )
                    pass


class Command(BaseCommand):
    """Link resubmissions, annotating with `resubmission_meta` data."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--audit_year",
            type=str,
            required=True,
            help="Audit year to process",
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

        parser.add_argument("--annotate_old", action="store_true")
        parser.set_defaults(annotate_old=False)

    def handle(self, *args, **options):
        # And, did they provide a staff user email?
        # (Note that they had to have privs in TF and be able to
        # enable SSH inproduction in order to get here.)
        try:
            ok_staff_user = StaffUser.objects.get(staff_email=options["email"])
        except StaffUser.DoesNotExist:
            logger.error(f'Staff user {options["email"]} does not exist')
            ok_staff_user = False
        if not ok_staff_user:
            sys.exit(-1)

        sorted_chains = [
            chain
            for chain in get_and_generate_submission_chains_by_equivalence(
                options["audit_year"], noisy=options["noisy"]
            )
            if len(chain) > 1
        ]

        export_chains_as_markdown(
            options["audit_year"], sorted_chains, noisy=options["noisy"]
        )

        export_chains_as_csv(
            options["audit_year"], sorted_chains, noisy=options["noisy"]
        )

        logger.info(f"Found {len(sorted_chains)} resubmission chains.")
        k = input("Review markdown/CSV and press `c` to continue...")
        if k != "c":
            logger.error("Exiting.")
            sys.exit()
        else:
            annotate_linked_reports(options, sorted_chains)

        if options["annotate_old"]:
            annotate_old(options)
