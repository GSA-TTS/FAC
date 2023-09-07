from django.db import models

class CognizantBaseline(models.Model):
    dbkey = models.CharField(
        "Identifier for a submission along with audit_year in Census FAC",
        null=True,
        max_length=20
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
        max_length=2,
    )

    date_assigned = models.DateTimeField(
        "Time when the cog agency was assigned to the entity"
    )
