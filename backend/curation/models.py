import logging

from django.db import models

from curation.management.commands.update_after_submission import validate_inputs
from .curationlib.update_after_submission import (
    update_uei,
    update_simple_gen_field,
)

logger = logging.getLogger(__name__)

EDITABLE_FIELDS = (("uei", "UEI"), ("ein", "EIN"), ("auditee_name", "Auditee Name"))


class EditRecord(models.Model):
    report_id = models.CharField(verbose_name="Report ID")
    field_to_edit = models.CharField(
        verbose_name="Field To Edit", choices=EDITABLE_FIELDS, default="uei"
    )
    old_value = models.CharField(
        verbose_name="Current Value To Change", null=True, blank=True
    )
    new_value = models.TextField(verbose_name="New Value", null=True, blank=True)

    editor_email = models.EmailField(verbose_name="Editor Email", null=True)
    edit_timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Edit Timestamp"
    )

    status = models.CharField(
        default="pending",
        choices=[("success", "Success"), ("failed", "Failed"), ("pending", "Pending")],
    )

    class Meta:
        verbose_name = "Edit Field Record"
        verbose_name_plural = "Edit Field Record"
        ordering = ["-edit_timestamp"]
        app_label = "curation"

    def __str__(self):
        return f"Edit of {self.field_to_edit} \
        for Report {self.report_id} \
        by {self.editor_email} on {self.edit_timestamp}"

    def create_options(self, *args, **kwargs):
        options = {
            "report_id": self.report_id,
            "email": self.editor_email,
            "old_uei": None,
            "new_uei": None,
            "old_ein": None,
            "new_ein": None,
            "old_auditee_name": None,
            "new_auditee_name": None,
            "old_authorization": None,
            "new_authorization": None,
        }
        if self.field_to_edit == "uei":
            options.update({"old_uei": self.old_value, "new_uei": self.new_value})
        elif self.field_to_edit == "ein":
            options.update(
                {
                    "old_ein": self.old_value,
                    "new_ein": self.new_value,
                }
            )
        elif self.field_to_edit == "auditee_name":
            options.update(
                {"old_auditee_name": self.old_value, "new_auditee_name": self.new_value}
            )
        else:
            logger.error(f"Invalid field_to_edit value: {self.field_to_edit}")
            self.status = "failed"
            super().save(*args, **kwargs)

        return options

    def save(self, *args, **kwargs):
        options = self.create_options(*args, **kwargs)

        try:
            if not validate_inputs(options):
                logger.error(
                    "Invalid inputs — check report_id, field selection, new value, and submission status."
                )
                self.status = "failed"
                super().save(*args, **kwargs)
                return
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            self.status = "failed"
            super().save(*args, **kwargs)
            return

        # Save the row NOW so Django's transaction closes before update_db opens its own
        self.status = "pending"
        super().save(*args, **kwargs)

        try:
            if self.field_to_edit == "uei":
                update_uei(options)
            elif self.field_to_edit == "ein":
                update_simple_gen_field(options, "ein")
            elif self.field_to_edit == "auditee_name":
                update_simple_gen_field(options, "auditee_name")
            else:
                raise ValueError(f"Invalid field_to_edit value: {self.field_to_edit}")
            self.status = "success"
        except Exception as e:
            logger.error(f"Update failed — type: {type(e).__name__}, message: {e}")
            self.status = "failed"

        super().save(update_fields=["status"])
