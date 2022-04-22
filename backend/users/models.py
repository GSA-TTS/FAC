from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)

    entry_form_data = models.JSONField(null=True, blank=True, help_text="Store of form data for Eligiblity, Info, and access steps prior to creation of an SF-SAC")

    def __str__(self):
        return self.user.email
