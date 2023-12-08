from django.apps import apps
from django.db import models
from django.db.models import Q
from django.utils import timezone


class CognizantBaseline(models.Model):
    dbkey = models.CharField(
        help_text="Identifier for a submission along with audit_year in Census FAC",
        null=True,
        max_length=20,
        verbose_name="dbkey",
    )
    ein = models.CharField(
        help_text="Primary Employer Identification Number",
        null=True,
        max_length=30,
        verbose_name="EIN",
    )
    uei = models.CharField(
        help_text="Unique Employer Identification Number",
        null=True,
        max_length=30,
        verbose_name="UEI",
    )
    cognizant_agency = models.CharField(
        help_text="Two digit Federal agency prefix of the cognizant agency",
        max_length=2,
        verbose_name="Cog Agency",
    )
    date_assigned = models.DateTimeField(
        help_text="Time when the cog agency was assigned to the entity",
        null=True,  # allow nulls in case history has nulls
        default=timezone.now,
        verbose_name="Date Assigned",
    )
    is_active = models.BooleanField(
        help_text="Record to be ignored if this field is False",
        default=True,
        verbose_name="Active",
    )
    source = models.CharField(
        help_text="Source of cognizant data",
        max_length=10,
        verbose_name="Source",
        default="GSAFAC",
    )


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

            uei, ein = sac.auditee_uei, sac.ein

            reset_baseline(cognizant_agency, ein, uei)

            try:
                gen_model = apps.get_model("dissemination.General")
                gen = gen_model.objects.get(report_id=sac.report_id)
                gen.cognizant_agency = cognizant_agency
                gen.save()
            except gen_model.DoesNotExist:
                # etl may not have been run yet
                pass

            super().save(*args, **kwargs)


def reset_baseline(cognizant_agency, ein, uei):
    baselines = CognizantBaseline.objects.filter(
        Q(is_active=True)
        & ~Q(cognizant_agency=cognizant_agency)
        & (Q(ein=ein) | Q(uei=uei))
    )
    for baseline in baselines:
        baseline.is_active = False
        baseline.save()
    existing_baseline_count = CognizantBaseline.objects.filter(
        Q(is_active=True)
        & Q(cognizant_agency=cognizant_agency)
        & (Q(ein=ein) | Q(uei=uei))
    ).count()
    if existing_baseline_count == 0:
        CognizantBaseline(
            ein=ein,
            uei=uei,
            cognizant_agency=cognizant_agency,
        ).save()
