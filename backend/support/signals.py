from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver

from audit.models import SingleAuditChecklist
from dissemination.models import General
from support.models import CognizantAssignment, CognizantBaseline
# from datetime import datetime 
from django.utils import timezone


@receiver(post_save, sender=CognizantAssignment)
def post_cog_assignment(sender, instance, created, **kwargs):
    """
    If a CognizantAssignment instance is saved, handle the effects this should
    have on other tables.
    """
    if created:
        sac = SingleAuditChecklist.objects.get(report_id=instance.report_id)
        cognizant_agency = sac.cognizant_agency

        ein, uei = sac.auditee_uei, sac.ein
        baselines = CognizantBaseline.objects.filter(Q(ein=ein) | Q(uei=uei))
        for baseline in baselines:
            baseline.is_active = False
            baseline.save()
        CognizantBaseline(
            ein=ein, uei=uei, cognizant_agency=cognizant_agency, date_assigned=timezone.now(), source="GSAFAC"
        ).save()

        try:
            gen = General.objects.get(report_id=sac.report_id)
            gen.cognizant_agency = cognizant_agency
            gen.save()
        except General.DoesNotExist:
            pass  # etl may not have been run yet
