from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CognizantAssignment
from .cog_over import propogate_cog_update


@receiver(post_save, sender=CognizantAssignment)
def create_user_profile(sender, instance, created, **kwargs):
    print("post save on cba")
    if created:
        propogate_cog_update(cog_assignment=instance)
