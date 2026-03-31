from django.contrib import admin
from .models import EditRecord
import subprocess

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
            "field_to_edit",
            "new_value",
            "editor_email",
        ]
        
    search_fields = (
        "report_id",
        "field_to_edit",
        "uei",
        "ein",
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
        print(f"Saving EditRecord: {request.user.email} Edited Report: {obj.report_id} for field: {obj.field_to_edit}")
        if obj.field_to_edit == 'uei':
            print(f"{obj.uei} -> {obj.new_value}")
        elif obj.field_to_edit == 'ein':
            print(f"{obj.ein} -> {obj.new_value}")
        else:
            raise ValueError("Invalid field_to_edit value")

        super().save_model(request, obj, form, change)
