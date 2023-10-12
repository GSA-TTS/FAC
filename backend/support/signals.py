from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver

from audit.models import SingleAuditChecklist
from dissemination.models import General
from support.models import CognizantAssignment, CognizantBaseline


@receiver(post_save, sender=CognizantAssignment)
def post_cog_assignment(sender, instance, created, **kwargs):
    """
    If a CognizantAssignment instance is saved, handle the effects this should
    have on other tables.
    """
    if created:
        cognizant_agency = instance.cognizant_agency
        sac = SingleAuditChecklist.objects.get(report_id=instance.report_id)
        sac.cognizant_agency = cognizant_agency
        sac.save()

        uei, ein = sac.auditee_uei, sac.ein

        reset_baseline(cognizant_agency, ein, uei)

        try:
            gen = General.objects.get(report_id=sac.report_id)
            gen.cognizant_agency = cognizant_agency
            gen.save()
        except General.DoesNotExist:
            # etl may not have been run yet
            pass


def reset_baseline(cognizant_agency, ein, uei):
    baselines = CognizantBaseline.objects.filter(
        Q(is_active=True)
        & ~Q(cognizant_agency=cognizant_agency)
        & (Q(ein=ein) | Q(uei=uei))
    )
    for baseline in baselines:
        baseline.is_active = False
        baseline.save()
    existing_baseline_count = CognizantBaseline.objects.filter(
        Q(is_active=True)
        & Q(cognizant_agency=cognizant_agency)
        & (Q(ein=ein) | Q(uei=uei))
    ).count()
    if existing_baseline_count == 0:
        CognizantBaseline(
            ein=ein,
            uei=uei,
            cognizant_agency=cognizant_agency,
        ).save()
