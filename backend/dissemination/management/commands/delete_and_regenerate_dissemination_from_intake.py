import logging
from django.core.management.base import BaseCommand
from dissemination.models import (
    AdditionalEin,
    AdditionalUei,
    CapText,
    FederalAward,
    Finding,
    FindingText,
    General,
    Note,
    Passthrough,
    SecondaryAuditor,
)
from audit.models import SingleAuditChecklist

logger = logging.getLogger(__name__)


def delete_everything_in_dissemination_model(model):
    model.objects.all().delete()


class Command(BaseCommand):
    """
    Deletes everything in `dissemination` tables and
    regenerates them from data in the intake tables.
    """

    help = """
    Deletes everything in `dissemination` tables and
    regenerates them from data in the intake tables.
    """

    dissemination_models = [
        AdditionalEin,
        AdditionalUei,
        CapText,
        FederalAward,
        Finding,
        FindingText,
        General,
        Note,
        Passthrough,
        SecondaryAuditor,
    ]

    def handle(self, *args, **_kwargs):
        logger.info("Re-running dissemination for all records.")

        # Begin by deleting all of the dissemination table contents.
        for model in Command.dissemination_models:
            logger.info("Deleting %s", model.__name__)
            delete_everything_in_dissemination_model(model)

        # Now, re-run dissemination for everything
        # in the intake tables.
        regen_statuses = (
            SingleAuditChecklist.STATUS.DISSEMINATED,
            SingleAuditChecklist.STATUS.SUBMITTED,
        )

        for sac in SingleAuditChecklist.objects.all():
            if sac.submission_status in regen_statuses:
                logger.info("Disseminating %s, ", sac.report_id)
                sac.disseminate()
