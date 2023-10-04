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
    SecondaryAuditor
)
from audit.models import (
    SingleAuditChecklist
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
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
        SecondaryAuditor
    ]

    def delete_everything_in_dissemination_model(self, model):
        model.objects.all().delete()

    def handle(self, *args, **kwargs):
        logger.info("Re-running dissemination for all records.")
        
        # Begin by deleting all of the dissemination table contents.
        for model in Command.dissemination_models:
            logger.info(f"Deleting {model.__name__}")
            self.delete_everything_in_dissemination_model(model)
    
        # Now, re-run dissemination for everything 
        # in the intake tables.
        for sac in SingleAuditChecklist.objects.all():
            if sac.submission_status == SingleAuditChecklist.STATUS.DISSEMINATED:
                logger.info(f"Disseminating {sac.report_id}")
                sac.disseminate()

