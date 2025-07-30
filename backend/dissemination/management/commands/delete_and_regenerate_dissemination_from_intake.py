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

        redisseminated = {}
        # FIXME: This wants to be __in (DISSEMINATED, REDISSEMINATED)
        for year in range(2015, date.today().year + 1):
            logger.info(f"Working year {year}")
            for sac in SingleAuditChecklist.objects.filter(
                submission_status=STATUS.DISSEMINATED,
                general_information__auditee_fiscal_period_end__startswith=f"{year}",
            ):
                logger.info(f"Redisseminating {sac.report_id}")
                sac.redisseminate()
                redisseminated[sac.report_id] = True

        # Repeat until we've redisseminated everything.
        # As long as something comes in, we do it again.
        changed = False
        while not changed:
            for year in range(2015, date.today().year + 1):
                logger.info(f"Re-working year {year}")
                for sac in SingleAuditChecklist.objects.filter(
                    submission_status=STATUS.DISSEMINATED,
                    general_information__auditee_fiscal_period_end__startswith=f"{year}",
                ):
                    if sac.report_id not in redisseminated:
                        logger.info(f"Double-check redisseminating {sac.report_id}")
                        sac.redisseminate()
                        changed = True
                        redisseminated[sac.report_id] = True
