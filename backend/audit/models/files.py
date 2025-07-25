import logging

from django.db import models
from django.contrib.auth import get_user_model
from audit.validators import (
    validate_excel_file,
    validate_single_audit_report_file,
    validate_component_page_numbers,
)


from .constants import STATUS

from .submission_event import SubmissionEvent
from .history import History

from ..exceptions import LateChangeError

User = get_user_model()


logger = logging.getLogger(__name__)


# TODO: Update Post SOC Launch: Update the Foreign keys, remove nullable
def excel_file_path(instance, _filename):
    """
    We want the actual filename in the filesystem to be unique and determined
    by report_id and form_section--not the user-provided filename.
    """
    return f"excel/{instance.sac.report_id}--{instance.form_section}.xlsx"


class ExcelFile(models.Model):
    """
    Data model to track uploaded Excel files and associate them with SingleAuditChecklists
    """

    file = models.FileField(upload_to=excel_file_path, validators=[validate_excel_file])
    filename = models.CharField(max_length=255)
    form_section = models.CharField(max_length=255)
    sac = models.ForeignKey("audit.SingleAuditChecklist", on_delete=models.CASCADE)
    audit = models.ForeignKey(
        "audit.Audit", on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.sac.submission_status != STATUS.IN_PROGRESS:
            raise LateChangeError("Attemtped Excel file upload")

        self.filename = f"{self.sac.report_id}--{self.form_section}.xlsx"

        event_user = kwargs.pop("event_user", None)
        event_type = kwargs.pop("event_type", None)

        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=self.sac, user=event_user, event=event_type
            )
            if self.audit:
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
    report_id = instance.sac.report_id
    return f"{base_path}/{report_id}.pdf"


class SingleAuditReportFile(models.Model):
    """
    Data model to track uploaded Single Audit report PDFs and associate them
    with SingleAuditChecklists
    """

    file = models.FileField(
        upload_to=single_audit_report_path,
        validators=[validate_single_audit_report_file],
    )
    filename = models.CharField(max_length=255)
    sac = models.ForeignKey("audit.SingleAuditChecklist", on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    audit = models.ForeignKey(
        "audit.Audit", on_delete=models.CASCADE, null=True, blank=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    component_page_numbers = models.JSONField(
        blank=True, null=True, validators=[validate_component_page_numbers]
    )

    def save(self, *args, **kwargs):
        report_id = self.sac.report_id
        self.filename = f"{report_id}.pdf"

        administrative_override = kwargs.pop("administrative_override", None)
        event_user = kwargs.pop("event_user", None)
        event_type = kwargs.pop("event_type", None)

        match self.sac.submission_status:
            # If we are in-progress, we may want to do something odd,
            # like override the filename. In that case, we'll do so,
            # and continue on through to save. Why? Because it is IN_PROGRESS.
            case STATUS.IN_PROGRESS:
                if administrative_override:
                    filename_override = kwargs.pop("filename_override", None)
                    if filename_override:
                        self.filename = filename_override
                    logger.info(
                        f"administrative override on SAR upload for {self.sac.report_id}"
                    )
            # If we are already DISSEMINATED, we should not be doing any editing.
            # The only way we will fall through this is if we have an administrative
            # override. That lets us edit/do a save. We do not
            # currently use this, but might in the future.
            case STATUS.DISSEMINATED:
                if administrative_override:
                    logger.info(
                        f"administrative override on SAR upload for {self.sac.report_id}"
                    )
                # Without an administrative override, this should be a late change
                # error. Throw it.
                else:
                    raise LateChangeError("Attempted PDF upload")
            # If we are NOT IN_PROGRESS, we should absolutely throw
            # a late change error. This is all other states.
            case _:
                raise LateChangeError("Attempted PDF upload")

        if event_user and event_type:
            self.user = event_user
            SubmissionEvent.objects.create(
                sac=self.sac, user=event_user, event=event_type
            )
            if self.audit:
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

        super().save()
