from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginGovUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    login_id = models.CharField(max_length=100, unique=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)

    entry_form_data = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="Store of form data for Eligiblity, Info, and access steps prior to creation of an SF-SAC",
    )

    def __str__(self):
        return self.user.email
