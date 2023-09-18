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
    # instance = kwargs["instance"]
    # import pdb
    #
    # pdb.set_trace()
    if created:
        sac = SingleAuditChecklist.objects.get(report_id=instance.report_id)
        cognizant_agency = instance.cognizant_agency
        sac.cognizant_agency = cognizant_agency
        sac.save()

        (ein, uei) = (sac.auditee_uei, sac.ein)
        baselines = CognizantBaseline.objects.filter(Q(ein=ein) | Q(uei=uei))
        for baseline in baselines:
            baseline.is_active = False
            baseline.save()
        CognizantBaseline(ein=ein, uei=uei, cognizant_agency=cognizant_agency).save()

        try:
            gen = General.objects.get(report_id=sac.report_id)
            gen.cognizant_agency = cognizant_agency
            gen.save()
        except General.DoesNotExist:
            pass  # etl may not have been run yet


# @receiver(post_save, sender=SingleAuditChecklist)
# def fac_post_process(sender, instance, _created, **kwargs):
#     sac: SingleAuditChecklist = instance
#     if sac.submission_status != SingleAuditChecklist.STATUS.SUBMITTED:
#         return
#     if sac.cognizant_agency or sac.oversight_agency:
#         return
#     assign_cog_over(sac)
