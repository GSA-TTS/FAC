from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT
from dissemination.models import docs


class SecondaryAuditor(models.Model):
    address_city = models.TextField(
        "CPA City",
        help_text=docs.auditor_city,
    )
    address_state = models.TextField(
        "CPA State",
        help_text=docs.auditor_state,
    )
    address_street = models.TextField(
        "CPA Street Address",
        help_text=docs.auditor_street1,
    )
    address_zipcode = models.TextField(
        "CPA Zip Code",
        help_text=docs.auditor_zip_code,
    )
    auditor_ein = models.TextField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        help_text=docs.auditor_ein,
    )
    auditor_name = models.TextField(
        "CPA Firm Name",
        help_text=docs.auditor_firm_name,
    )
    contact_email = models.TextField(
        "CPA mail address (optional)",
        help_text=docs.auditor_email,
    )
    contact_name = models.TextField(
        "Name of CPA Contact",
    )
    contact_phone = models.TextField(
        "CPA phone number",
        help_text=docs.auditor_phone,
    )
    contact_title = models.TextField(
        "Title of CPA Contact",
        help_text=docs.auditor_title,
    )
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
