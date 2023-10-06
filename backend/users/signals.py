from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile, StaffUser

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        staff_emails = StaffUser.objects.all().values("staff_email")
        if instance.email in staff_emails:
            instance.is_staff = True
            instance.save()
