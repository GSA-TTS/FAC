from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import (
    SingleAuditChecklist,
    SubmissionEvent,
)


User = get_user_model()


class AccessManager(models.Manager):
    """Custom manager for Access."""

    def create(self, **obj_data):
        """
        Check for existing users and add them at access creation time.
        Not doing this would mean that users logged in at time of Access
        instance creation would have to log out and in again to get the new
        access.
        """

        # remove event_user & event_type keys so that they're not passed into super().create below
        event_user = obj_data.pop("event_user", None)
        event_type = obj_data.pop("event_type", None)

        if obj_data["email"]:
            try:
                acc_user = User.objects.get(email=obj_data["email"])
            except User.DoesNotExist:
                acc_user = None
            if acc_user:
                obj_data["user"] = acc_user
        result = super().create(**obj_data)

        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=result.sac,
                user=event_user,
                event=event_type,
            )

        return result


class Access(models.Model):
    """
    Email addresses which have been granted access to SAC instances.
    An email address may be associated with a User ID if an FAC account exists.
    """

    objects = AccessManager()

    ROLES = (
        ("certifying_auditee_contact", _("Auditee Certifying Official")),
        ("certifying_auditor_contact", _("Auditor Certifying Official")),
        ("editor", _("Audit Editor")),
    )
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    role = models.CharField(
        choices=ROLES,
        help_text="Access type granted to this user",
        max_length=50,
    )
    fullname = models.CharField(blank=True)
    email = models.EmailField()
    user = models.ForeignKey(
        User,
        null=True,
        help_text="User ID associated with this email address, empty if no FAC account exists",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.email} as {self.get_role_display()}"

    class Meta:
        """Constraints for certifying roles"""

        verbose_name_plural = "accesses"

        constraints = [
            # a SAC cannot have multiple certifying auditees
            models.UniqueConstraint(
                fields=["sac"],
                condition=Q(role="certifying_auditee_contact"),
                name="%(app_label)s_$(class)s_single_certifying_auditee",
            ),
            # a SAC cannot have multiple certifying auditors
            models.UniqueConstraint(
                fields=["sac"],
                condition=Q(role="certifying_auditor_contact"),
                name="%(app_label)s_%(class)s_single_certifying_auditor",
            ),
        ]
