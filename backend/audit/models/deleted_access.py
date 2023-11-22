from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from .access import Access
from .models import SingleAuditChecklist


User = get_user_model()


class DeletedAccess(models.Model):
    """
    Record of Access entries that have been deleted
    """

    class RemovalEventType:
        """
        We only have one now, but in future may expand this to include
        account-inactivity, security-incident, etc.
        """

        ACCESS_CHANGE = "access-change"

    EVENT_TYPES = ((RemovalEventType.ACCESS_CHANGE, _("Access change")),)

    # The first five fields are identical to Access:
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    role = models.CharField(
        choices=Access.ROLES,
        help_text="Access type granted to this user",
        max_length=50,
    )
    fullname = models.CharField(blank=True)
    email = models.EmailField()
    user = models.ForeignKey(
        User,
        null=True,
        help_text=(
            "User ID associated with this email address, "
            "empty if no FAC account exists"
        ),
        on_delete=models.PROTECT,
    )
    # The next four fields are metadata about the deletion:
    removed_at = models.DateTimeField(auto_now_add=True)
    removed_by_user = models.ForeignKey(
        User,
        # Nullable because in future we may have system-initiated deletions:
        null=True,
        help_text="User ID used to delete this Access",
        on_delete=models.PROTECT,
        related_name="access_deleted",
    )
    removed_by_email = models.EmailField()
    removal_event = models.CharField(choices=EVENT_TYPES)

    def __str__(self):
        email = self.email
        role = self.get_role_display()
        del_by = self.removed_by_email
        del_at = self.removed_at
        return f"{email} as {role} deleted by {del_by} at {del_at}"

    class Meta:
        """
        Ensure plural doesn't show as "deletedaccesss".
        """

        verbose_name_plural = "deleted accesses"
