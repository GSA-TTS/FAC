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
from audit.models.constants import STATUS
from datetime import date

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Regenerates all dissemination_ records from SingleAuditChecklist.
    Does this one record at a time; can be run while the system is operating.

    Optionally, use `--report_id` to attempt to force the redissemination of a particular record.
    Useful for debugging.
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

    def add_arguments(self, parser):
        parser.add_argument(
            "--report_id",
            type=str,
            help="The ID of the SAC.",
            default=None,
        )

    def handle(self, *args, **_kwargs):
        report_id = _kwargs.get("report_id")

        if report_id:
            try:
                sac = SingleAuditChecklist.objects.get(report_id=report_id)
                sac.redisseminate()
                exit(0)
            except SingleAuditChecklist.DoesNotExist:
                logger.info(f"No report with report_id found: {report_id}")
                exit(-1)

        logger.info("Re-running dissemination for all records.")

        redisseminated = {}
        for year in range(2015, date.today().year + 1):
            logger.info(f"Working year {year}")
            for sac in SingleAuditChecklist.objects.filter(
                submission_status__in=[STATUS.DISSEMINATED, STATUS.RESUBMITTED],
                general_information__auditee_fiscal_period_end__startswith=f"{year}",
            ):
                logger.info(f"Redisseminating {sac.report_id}")
                sac.redisseminate()
                redisseminated[sac.report_id] = True
