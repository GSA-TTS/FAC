from django.contrib import admin
from .models import EditRecord

import logging

logger = logging.getLogger(__name__)


class SupportAdmin(admin.ModelAdmin):
    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EditRecord)
class EditRecordAdmin(SupportAdmin):
    date_hierarchy = "edit_timestamp"
    ordering = ["edit_timestamp"]

    list_display = [
        "report_id",
        "uei",
        "ein",
        "auditee_name",
        "field_to_edit",
        "new_value",
        "editor_email",
        "edit_timestamp",
        "status",
    ]
    list_filter = [
        "report_id",
        "uei",
        "ein",
        "auditee_name",
        "field_to_edit",
        "new_value",
        "editor_email",
    ]

    search_fields = (
        "report_id",
        "field_to_edit",
        "uei",
        "ein",
        "auditee_name",
        "new_value",
        "editor_email",
    )

    readonly_fields = ["editor_email", "edit_timestamp", "status"]

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff

    def save_model(self, request, obj, form, change):
        obj.editor_email = request.user.email
        logger.info(
            f"EditRecord saved: {request.user.email} edited report {obj.report_id}, field: {obj.field_to_edit}"
        )
        super().save_model(request, obj, form, change)
