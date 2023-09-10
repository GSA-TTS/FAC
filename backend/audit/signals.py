from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SingleAuditChecklist
from support import cog_over


@receiver(post_save, sender=SingleAuditChecklist)
def fac_post_process(sender, instance, created, **kwargs):
    sac: SingleAuditChecklist = instance
    if sac.submission_status != SingleAuditChecklist.STATUS.SUBMITTED:
        return
    cog_over.assign_cog_over(sac)
