from audit.models import (
    SingleAuditChecklist,
    SubmissionEvent,
    User,
)
from audit.models.constants import RESUBMISSION_STATUS
from users.models import StaffUser
from audit.models.constants import STATUS
from django.db import transaction

from curation.curationlib.generate_resubmission_clusters import (
    generate_resbmission_clusters,
)
from curation.curationlib.export_resubmission_clusters import (
    # export_sets_as_text_tables,
    export_sets_as_csv,
    export_sets_as_markdown,
    order_reports_key,
)

from django.core.management.base import BaseCommand
import sys

import logging

logger = logging.getLogger(__name__)


def lfilter(fun, ls):
    return list(filter(fun, ls))


def point_old_to_new(
    first: SingleAuditChecklist, second: SingleAuditChecklist, u: User
):
    # Points the first at the second, where the first
    # is the older of the two audits.

    # If the first has no resubmission metadata, it must be the first in a chain.
    # This is like calling 'initiate_resubmission' on an audit.
    if first.resubmission_meta is None:
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
            # Once we modify the records, we need to redisseminate
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


def annotate_linked_reports(options, sorted_sets):
    u = User.objects.get(email=options["email"])
    for linked in sorted_sets:
        # Order the sets internally by their first submitted transition.
        # These are SAC records.
        linked_sorted = sorted(linked, key=order_reports_key)
        # Now, each element wants to link to the next and previous.
        the_length = len(linked_sorted)
        # range() is from [0, length) (inclusive, exclusive)
        for ndx in range(the_length - 1):
            # I want to link this to next, and visa-versa.
            this_ndx = ndx
            next_ndx = ndx + 1
            # Are they both less than the length? If so, they can be linked.
            if this_ndx < the_length and next_ndx <= the_length:
                try:
                    this_sac = linked_sorted[this_ndx]
                    next_sac = linked_sorted[next_ndx]
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

        sorted_sets = lfilter(
            lambda s: len(s) > 1,
            generate_resbmission_clusters(
                options["audit_year"], noisy=options["noisy"]
            ),
        )

        export_sets_as_markdown(
            options["audit_year"], sorted_sets, noisy=options["noisy"]
        )

        export_sets_as_csv(options["audit_year"], sorted_sets, noisy=options["noisy"])

        k = input("Review markdown and press `c` to continue...")
        if k != "c":
            logger.error("Exiting.")
            sys.exit()
        else:
            annotate_linked_reports(options, sorted_sets)

        if options["annotate_old"]:
            annotate_old(options)
