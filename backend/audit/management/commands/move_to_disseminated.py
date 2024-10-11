"""
Allows the manual transition of an audit to dissemination.
"""

from audit.models import (
    SingleAuditChecklist,
)
from audit.models.models import STATUS
from audit.models.viewflow import sac_revert_from_submitted, sac_transition
from curation.curationlib.curation_audit_tracking import (
    enable_audit_curation,
    disable_audit_curation,
)
from dissemination.remove_workbook_artifacts import remove_workbook_artifacts
from django.core.management.base import BaseCommand
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for disseminating an audit.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--report_id",
            type=str,
            help="The ID of the SAC.",
            default=None,
        )

    def handle(self, *args, **options):
        report_id = options.get("report_id")

        # no parameter passed.
        if report_id is None:
            logger.info(
                "No report_id supplied. (move_to_disseminated --report_id ID_OF_REPORT)"
            )
            exit(-1)

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
        except SingleAuditChecklist.DoesNotExist:
            logger.info(f"No report with report_id found: {report_id}")
            exit(-1)

        # must be stuck as 'submitted'.
        if sac.submission_status != STATUS.SUBMITTED:
            logger.info(
                f"Unable to disseminate report that is not in submitted state: {report_id}"
            )
            exit(-1)

        # check for validation errors.
        errors = sac.validate_full()
        if errors:
            logger.info(
                f"Unable to disseminate report with validation errors: {report_id}."
            )
            logger.info(errors["errors"])

            # return to auditee_certified.
            sac_revert_from_submitted(sac)
            logger.info(f"Returned report to auditee_certified state: {report_id}")
            exit(0)

        # BEGIN ATOMIC BLOCK
        enable_audit_curation()
        with transaction.atomic():
            disseminated = sac.disseminate()
            # `disseminated` is None if there were no errors.
            if disseminated is None:
                sac_transition(None, sac, transition_to=STATUS.DISSEMINATED)
        # END ATOMIC BLOCK
        disable_audit_curation()

        # IF THE DISSEMINATION SUCCEEDED
        # `disseminated` is None if there were no errors.
        if disseminated is None:
            # Remove workbook artifacts after the report has been disseminated.
            # We do this outside of the atomic block. No race between
            # two instances of the FAC should be able to get to this point.
            # If we do, something will fail.
            remove_workbook_artifacts(sac)

        # IF THE DISSEMINATION FAILED
        # If disseminated has a value, it is an error
        # object returned from `sac.disseminate()`
        if disseminated is not None:
            logger.info(
                "{} is a `not None` value report_id[{}] for `disseminated`".format(
                    disseminated, report_id
                )
            )

            # return to auditee_certified.
            sac_revert_from_submitted(sac)
            exit(0)

        logger.info(f"DISSEMINATED REPORT: {report_id}")
        exit(0)
