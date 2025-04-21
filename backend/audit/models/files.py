import logging

from django.db import models
from django.contrib.auth import get_user_model
from audit.validators import (
    validate_excel_file,
    validate_single_audit_report_file,
    validate_component_page_numbers,
)


from .constants import STATUS

from .history import History

from ..exceptions import LateChangeError

User = get_user_model()


logger = logging.getLogger(__name__)


def excel_file_path(instance, _filename):
    """
    We want the actual filename in the filesystem to be unique and determined
    by report_id and form_section--not the user-provided filename.
    """
    return f"excel/{instance.audit.report_id}--{instance.form_section}.xlsx"


class ExcelFile(models.Model):
    """
    Data model to track uploaded Excel files and associate them with Audits
    """

    file = models.FileField(upload_to=excel_file_path, validators=[validate_excel_file])
    filename = models.CharField(max_length=255)
    form_section = models.CharField(max_length=255)
    audit = models.ForeignKey("audit.Audit", on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.audit.submission_status != STATUS.IN_PROGRESS:
            raise LateChangeError("Attemtped Excel file upload")

        self.filename = f"{self.audit.report_id}--{self.form_section}.xlsx"

        event_user = kwargs.pop("event_user", None)
        event_type = kwargs.pop("event_type", None)

        if event_user and event_type:
            History.objects.create(
                report_id=self.audit.report_id,
                version=self.audit.version,
                updated_by=event_user,
                event=event_type,
                event_data={
                    "form_section": self.form_section,
                    "filename": self.filename,
                },
            )

        super().save(*args, **kwargs)


def single_audit_report_path(instance, _filename):
    """
    We want the actual filename in the filesystem to be unique and determined
    by report_id, not the user-provided filename.
    """
    base_path = "singleauditreport"
    report_id = instance.audit.report_id
    return f"{base_path}/{report_id}.pdf"


class SingleAuditReportFile(models.Model):
    """
    Data model to track uploaded Single Audit report PDFs and associate them
    with Audits
    """

    file = models.FileField(
        upload_to=single_audit_report_path,
        validators=[validate_single_audit_report_file],
    )
    filename = models.CharField(max_length=255)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    audit = models.ForeignKey("audit.Audit", on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)
    component_page_numbers = models.JSONField(
        blank=True, null=True, validators=[validate_component_page_numbers]
    )

    def save(self, *args, **kwargs):
        report_id = self.audit.report_id
        self.filename = f"{report_id}.pdf"
        if self.audit.submission_status != STATUS.IN_PROGRESS:
            raise LateChangeError("Attempted PDF upload")

        event_user = kwargs.pop("event_user", None)
        event_type = kwargs.pop("event_type", None)
        if event_user and event_type:
            self.user = event_user
            History.objects.create(
                report_id=self.audit.report_id,
                version=self.audit.version,
                updated_by=event_user,
                event=event_type,
                event_data={
                    "component_page_numbers": self.component_page_numbers,
                    "filename": self.filename,
                },
            )

        super().save(*args, **kwargs)
