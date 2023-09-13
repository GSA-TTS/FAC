from django.contrib import admin

from .models import CognizantBaseline, CognizantAssignment


class SupportAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        if request.user.is_staff:
            return True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
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
    ]
    list_filter = [
        "is_active",
        "uei",
        "cognizant_agency",
        "ein",
    ]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CognizantAssignment)
class CognizantAssignmentAdmin(SupportAdmin):
    date_hierarchy = "date_assigned"
    ordering = ["date_assigned"]
    list_display = [
        "report_id",
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

    def report_id(self, ca):
        return ca.sac.report_id

    def has_add_permission(self, request, obj=None):
        if request.user.is_staff:
            return True
