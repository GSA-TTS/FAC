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

    fieldsets = (
        (
            None,
            {
                "description": (
                    "<strong>Instructions:</strong> Please fill in all fields carefully. "
                    "The form can only edit an audit record that is disseminated. Please ensure the report ID is correct and the current value matches what is in the system."
                ),
                "fields": ("report_id", "field_to_edit", "old_value", "new_value"),
            },
        ),
    )

    date_hierarchy = "edit_timestamp"
    ordering = ["edit_timestamp"]

    list_display = [
        "report_id",
        "field_to_edit",
        "old_value",
        "new_value",
        "editor_email",
        "edit_timestamp",
        "status",
    ]
    list_filter = [
        "report_id",
        "field_to_edit",
        "old_value",
        "new_value",
        "editor_email",
    ]

    search_fields = (
        "report_id",
        "field_to_edit",
        "old_value",
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
