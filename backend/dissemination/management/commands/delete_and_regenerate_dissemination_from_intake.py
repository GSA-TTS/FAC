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

    --report_id (optional): Redisseminate a single report_id
    --year (optional): Redisseminate a single audit year
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
        parser.add_argument(
            "--year",
            type=str,
            help="The year to process.",
            default=None,
        )

    def handle(self, *args, **_kwargs):
        report_id = _kwargs.get("report_id")
        year = _kwargs.get("year")

        if report_id and year:
            logger.error("Only one of --report_id or --year can be provided. Exiting.")
            exit(-1)

        if report_id:
            logger.info(f"Redisseminating {report_id}.")

            try:
                sac = SingleAuditChecklist.objects.get(report_id=report_id)
                sac.redisseminate()
                logger.info(f"Redisseminated: {report_id}.")
                exit(0)
            except SingleAuditChecklist.DoesNotExist:
                logger.error(f"No report with report_id found: {report_id}. Exiting.")
                exit(-1)
        else:
            if year:
                years = [year]
            else:
                logger.info("Redisseminating all records.")
                years = range(2015, date.today().year + 1)

            redisseminated = {}

            for year in years:
                logger.info(f"Working year {year}")

                for sac in SingleAuditChecklist.objects.filter(
                    submission_status__in=[STATUS.DISSEMINATED, STATUS.RESUBMITTED],
                    general_information__auditee_fiscal_period_end__startswith=f"{year}",
                ):
                    logger.info(f"Redisseminating {sac.report_id}.")
                    sac.redisseminate()
                    redisseminated[sac.report_id] = True

        logger.info("Redisseminating complete.")
