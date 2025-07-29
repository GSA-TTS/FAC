from django.db import models


class WaiverType(models.TextChoices):
    AUDITEE_CERTIFYING_OFFICIAL = (
        "auditee_certifying_official",
        "No auditee certifying official is available",
    )
    AUDITOR_CERTIFYING_OFFICIAL = (
        "auditor_certifying_official",
        "No auditor certifying official is available",
    )
    ACTIVE_UEI = (
        "active_uei",
        "The auditee cannot activate their SAM.gov UEI registration",
    )
