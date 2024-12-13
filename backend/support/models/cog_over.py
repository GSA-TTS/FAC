from django.apps import apps
from django.db import models


class AssignmentTypeCode:
    COMPUTED = "computed"
    MANUAL = "manual"


ASSIGNMENT_TYPES = (
    (AssignmentTypeCode.COMPUTED, "Computed by FAC"),
    (AssignmentTypeCode.MANUAL, "Manual Override"),
)


class CognizantAssignment(models.Model):
    report_id = models.CharField()
    cognizant_agency = models.CharField(
        # "Two digit Federal agency prefix of the cognizant agency",
        max_length=2,
        verbose_name="Cog Agency",
    )
    date_assigned = models.DateTimeField(
        # "Time when the cog agency was assigned to the entity",
        auto_now_add=True,
        verbose_name="Date Assigned",
    )
    assignor_email = models.EmailField(
        # "Who originally set the cog agency or who overrode it",
        verbose_name="Email",
    )
    override_comment = models.TextField(
        # "Comment by assignor explaining the justification for an override",
        verbose_name="Comment",
    )
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPES,
        default=AssignmentTypeCode.COMPUTED,
        verbose_name="Type",
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            sac_model = apps.get_model("audit.SingleAuditChecklist")
            cognizant_agency = self.cognizant_agency
            sac = sac_model.objects.get(report_id=self.report_id)
            sac.cognizant_agency = cognizant_agency
            sac.save()

            try:
                gen_model = apps.get_model("dissemination.General")
                gen = gen_model.objects.get(report_id=sac.report_id)
                gen.cognizant_agency = cognizant_agency
                gen.save()
            except gen_model.DoesNotExist:
                # etl may not have been run yet
                pass

            super().save(*args, **kwargs)
