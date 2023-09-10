from django.db import models

from audit.models import SingleAuditChecklist


class CognizantBaseline(models.Model):
    dbkey = models.CharField(
        "Identifier for a submission along with audit_year in Census FAC",
        null=True,
        max_length=20,
    )
    ein = models.CharField(
        "Primary Employer Identification Number",
        null=True,
        max_length=30,
    )
    uei = models.CharField(
        "Unique Employer Identification Number",
        null=True,
        max_length=30,
    )
    cognizant_agency = models.CharField(
        "Two digit Federal agency prefix of the cognizant agency",
        null=True,
        max_length=2,
    )
    date_assigned = models.DateTimeField(
        "Time when the cog agency was assigned to the entity",
        null=True,
    )
    is_active = models.BooleanField(
        "Record to be ignored if this field is False",
        null=True,
        default=True,
    )


class AssignmentTypeCode:
    COMPUTED = "computed"
    MANUAL = "manual"


ASSIGNMENT_TYPES = (
    (AssignmentTypeCode.COMPUTED, "Computed by FAC"),
    (AssignmentTypeCode.MANUAL, "Manual Override"),
)


class CognizantAssignment(models.Model):
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    cognizant_agency = models.CharField(
        "Two digit Federal agency prefix of the cognizant agency",
        null=True,
        max_length=2,
    )
    date_assigned = models.DateTimeField(
        "Time when the cog agency was assigned to the entity",
        null=True,
        auto_now_add=True,
    )
    assignor_email = models.EmailField(
        "Who originally set the cog agency or who overrode it",
        null=True,
    )
    override_comment = models.TextField(
        "Comment by assignor explaining the justification for an override",
        null=True,
    )
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPES,
        default=AssignmentTypeCode.COMPUTED,
        null=True,
    )

    # def save(self, *args, **kwargs):
    #     request = kwargs["request"]
    #     self.assignor_email = request.user.email
    #     super().save(*args, **kwargs)
