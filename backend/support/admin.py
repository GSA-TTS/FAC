from django.contrib import admin

from audit.models import SingleAuditChecklist
from .models import CognizantBaseline, CognizantAssignment, AssignmentTypeCode


class SupportAdmin(admin.ModelAdmin):
    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CognizantBaseline)
class CognizantBaselineAdmin(SupportAdmin):
    list_display = [
        "uei",
        "cognizant_agency",
        "date_assigned",
        "ein",
        "dbkey",
        "is_active",
        "source",
    ]
    list_filter = [
        "source",
        "is_active",
        "cognizant_agency",
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CognizantAssignment)
class CognizantAssignmentAdmin(SupportAdmin):
    date_hierarchy = "date_assigned"
    ordering = ["date_assigned"]
    list_display = [
        "report_id",
        "uei",
        "cognizant_agency",
        "date_assigned",
        "assignor_email",
        "override_comment",
        "assignment_type",
    ]
    list_filter = [
        "assignment_type",
        "cognizant_agency",
    ]
    fields = [
        "report_id",
        (
            "uei",
            "last_assigned_by",
            "current_cog",
        ),
        "cognizant_agency",
        "override_comment",
    ]
    readonly_fields = [
        "uei",
        "last_assigned_by",
        "current_cog",
    ]

    def uei(self, obj):
        return SingleAuditChecklist.objects.get(report_id=obj.report_id).auditee_uei

    def current_cog(self, obj):
        return SingleAuditChecklist.objects.get(
            report_id=obj.report_id
        ).cognizant_agency

    def last_assigned_by(self, obj):
        return obj.assignor_email

    save_as = True
    save_as_continue = False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """customize edit form"""
        extra_context = extra_context or {}
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = False
        extra_context[
            "show_save_and_add_another"
        ] = False  # this does not work if has_add_permision is True
        return super().change_view(request, object_id, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        obj.assignor_email = request.user.email
        obj.assignment_type = AssignmentTypeCode.MANUAL
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff
