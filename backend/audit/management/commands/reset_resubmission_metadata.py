import logging
import sys

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db import transaction

from audit.models import SingleAuditChecklist, SubmissionEvent, User
from audit.models.constants import STATUS
from users.models import StaffUser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Reset resubmission metadata to defaults. Operates on either a full audit year or a list of report_ids.
    """

    def add_arguments(self, parser):
        scope = parser.add_mutually_exclusive_group(required=True)
        scope.add_argument(
            "--audit_year",
            type=str,
            help="Audit year to process",
        )
        scope.add_argument(
            "--report_ids",
            type=str,
            nargs="+",  # Appends the following arguments as a list
            metavar="report_id",
            help="One or more specific report IDs to reset",
        )
        parser.add_argument(
            "--email",
            type=str,
            required=True,
            help="The email of the FAC staff running this command",
        )

    def handle(self, *args, **options):
        # Verify staff user. Note that it's VERY hard to get here without already being staff.
        try:
            ok_staff_user = StaffUser.objects.get(staff_email=options["email"])
        except StaffUser.DoesNotExist:
            logger.error(f'Staff user {options["email"]} does not exist')
            ok_staff_user = False
        if not ok_staff_user:
            sys.exit(-1)

        # AY or a list of ID's. The report_id's will be run regardless of resubmission linkage - that specifically is dangerous.
        if options["audit_year"]:
            audit_year = options["audit_year"]
            sacs = list(
                SingleAuditChecklist.objects.filter(
                    Q(
                        general_information__auditee_fiscal_period_end__startswith=audit_year
                    )
                    & Q(resubmission_meta__isnull=False)
                )
            )
            label = f"AY{audit_year}"
        else:
            report_ids = options["report_ids"]
            sacs = list(
                SingleAuditChecklist.objects.filter(
                    Q(report_id__in=report_ids) & Q(resubmission_meta__isnull=False)
                )
            )
            label = f"report IDs: {', '.join(report_ids)}"
            # Warn about any IDs that were not found or had no metadata.
            found_ids = {sac.report_id for sac in sacs}
            missing = set(report_ids) - found_ids
            if missing:
                logger.warning(
                    f"The following report IDs were not found or have no "
                    f"resubmission metadata and will be skipped: {missing}"
                )

        if not sacs:
            logger.info(f"No submissions with resubmission metadata found for {label}.")
            sys.exit(0)

        logger.info(f"Found {len(sacs)} submissions for {label}.")

        k = input("\nPress `c` to continue...")
        if k != "c":
            logger.error("Exiting.")
            sys.exit()

        ok_user = User.objects.get(email=options["email"])
        reset_count = 0

        for sac in sacs:
            sac.resubmission_meta = {
                "version": 0,
                "resubmission_status": "no_resubmission_data",
            }
            sac.submission_status = STATUS.DISSEMINATED

            with transaction.atomic():
                sac.save(
                    administrative_override=True,
                    event_user=ok_user,
                    event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_RESUBMISSION_ANNOTATION,
                )
                sac.redisseminate()

            reset_count += 1

        logger.info(
            f"\nReset complete. {reset_count} submissions cleared and redisseminated."
        )
