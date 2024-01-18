from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as DjangoUser
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.db.models import Q
from .access_roles import ACCESS_ROLES
from .deleted_access import DeletedAccess
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

        # try to pair this Access with an actual User object if we have one for this email address
        if obj_data["email"]:
            try:
                acc_user = User.objects.get(email__iexact=obj_data["email"])
            # if we don't have a User for this email, leave it as None (unclaimed Access)
            except User.DoesNotExist:
                acc_user = None
            # if we have multiple Users for this email, leave it as None
            # this typically happens if a user deletes their Login.gov account
            # and creates a new one using the same email address.
            # In this case we want to defer assigning this Access to a specific
            # User until the next time they login to the FAC, because we don't
            # yet know which of their User accounts is the "active" one
            except MultipleObjectsReturned:
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

    ROLES = ACCESS_ROLES
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

    def delete(self, *args, **kwds):
        """
        Override method to create DeletedAccess entries upon deletion.

        Returns only the result of the Access deletion to maintain compatibility with
        what all other delete methods return.
        """
        removing_user = kwds.get("removing_user")
        removal_event = kwds.get("removal_event", "access-change")
        access_deletion_return, _deletion_record = delete_access_and_create_record(
            self, removing_user, removal_event
        )
        return access_deletion_return

    def get_friendly_role(self) -> str | None:
        """Return the friendly version of the role."""
        return dict(self.ROLES)[self.role]

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


def remove_email_from_submission_access(
    report_id: str,
    email: str,
    role: str,
    removing_user: DjangoUser = None,
    event: str = "access-change",
) -> list[tuple[tuple[int, dict], DeletedAccess]]:
    """
    Given report_id, email address and role, deletes corresponding Access objects
    and creates corresponding DeletedAccess objects.
    Will raise SingleAuditChecklist.DoesNotExist if no matching SAC exists.
    Will raise Access.DoesNotExist if no matching Access objects exist.
    """
    sac = SingleAuditChecklist.objects.get(report_id=report_id)
    accesses = Access.objects.filter(sac=sac, email=email, role=role)
    if len(accesses) < 1:
        raise Access.DoesNotExist
    deletion_records: list[tuple[tuple[int, dict], DeletedAccess]] = []
    for access in accesses:
        result_pair = delete_access_and_create_record(access, removing_user, event)
        deletion_records.append(result_pair)
    return deletion_records


def delete_access_and_create_record(
    access: Access, removing_user: DjangoUser = None, event: str = "access-change"
) -> tuple[tuple[int, dict], DeletedAccess]:
    """
    Given an Access object, delete that object and created a corresponding
    DeletedAccess object.
    """
    removed_by_email = removing_user.email if removing_user else None
    deletion_record = DeletedAccess(
        sac=access.sac,
        role=access.role,
        fullname=access.fullname,
        email=access.email,
        user=access.user,
        removed_by_user=removing_user,
        removed_by_email=removed_by_email,
        removal_event=event,
    )
    deletion_record.save()
    access_deletion_return = super(Access, access).delete()
    return (access_deletion_return, deletion_record)
