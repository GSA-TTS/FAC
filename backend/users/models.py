from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Permission(models.Model):
    class PermissionType:
        READ_TRIBAL = "read-tribal"

    PERMISSION_CHOICES = ((PermissionType.READ_TRIBAL, _("Read tribal audit data")),)

    slug = models.CharField(max_length=255, choices=PERMISSION_CHOICES, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.slug


class UserPermission(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    permission = models.ForeignKey(Permission, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("user", "permission")


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


class StaffUser(models.Model):
    """
    List of email addresses maintained by a superuser using an admin screen.
    When a login email matches an entry here, the corresponding user is upgraded to a staff user.
    Should have only one active row per staff_email.
    """

    staff_email = models.EmailField()
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Added",
    )
    added_by_email = models.EmailField(
        verbose_name="Email of Adder",
    )

    def save(self, *args, **kwargs):
        """Add a new staffuser based on email."""

        User.objects.filter(email=self.staff_email).update(is_staff=True)
        super(StaffUser, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Removes any user associated with an email as a staffuser."""

        User.objects.filter(email=self.staff_email).update(
            is_staff=False, is_superuser=False
        )
        super(StaffUser, self).delete(*args, **kwargs)


class StaffUserLog(models.Model):
    """
    Tracks removals from StaffUser
    A row is inserted whenever StaffUser is deleted in admin.py
    """

    staff_email = models.EmailField()
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Added",
    )
    added_by_email = models.EmailField(
        verbose_name="Email of Adder",
    )
    date_removed = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date removed",
    )
    removed_by_email = models.EmailField(
        verbose_name="Email of Remover",
    )
