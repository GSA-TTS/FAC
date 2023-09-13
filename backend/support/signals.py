from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CognizantAssignment
from audit.models import SingleAuditChecklist
from .cog_over import propogate_cog_update, assign_cog_over


@receiver(post_save, sender=CognizantAssignment)
def post_cog_assignment(sender, instance, created, **kwargs):
    if created:
        propogate_cog_update(cog_assignment=instance)


@receiver(post_save, sender=SingleAuditChecklist)
def fac_post_process(sender, instance, created, **kwargs):
    sac: SingleAuditChecklist = instance
    if sac.submission_status != SingleAuditChecklist.STATUS.SUBMITTED:
        return
    if sac.cognizant_agency or sac.oversight_agency:
        return
    assign_cog_over(sac)
