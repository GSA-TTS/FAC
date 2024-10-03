"""
Allows the manual transition of an audit to dissemination.
"""
from audit.models import (
    SingleAuditChecklist,
)
from audit.models.models import STATUS
from audit.models.viewflow import sac_transition
from dissemination.remove_workbook_artifacts import remove_workbook_artifacts
from django.core.management.base import BaseCommand
from django.db import transaction
from django.shortcuts import get_object_or_404

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
            logger.error('You need to enter a report_id (--report_id ID_OF_REPORT).')
            exit(0)

        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)

        # must be stuck as 'submitted'.
        if sac.submission_status != STATUS.SUBMITTED:
            logger.error('This report is not stuck in the submitted state.')
            exit(0)

        # BEGIN ATOMIC BLOCK
        with transaction.atomic():
            disseminated = sac.disseminate()
            # `disseminated` is None if there were no errors.
            if disseminated is None:
                sac_transition(None, sac, transition_to=STATUS.DISSEMINATED)
        # END ATOMIC BLOCK

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
            
        logger.info(f"Disseminated report: {report_id}")
