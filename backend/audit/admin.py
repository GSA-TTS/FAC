from django.contrib import admin
from audit.models import (
    Access,
    DeletedAccess,
    ExcelFile,
    SingleAuditChecklist,
    SingleAuditReportFile,
    SubmissionEvent,
)


class SACAdmin(admin.ModelAdmin):
    """
    Support for read-only staff access, and control of what fields are present and
    filterable/searchable.
    """

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "id",
        "report_id",
        "cognizant_agency",
        "oversight_agency",
    )
    list_filter = [
        "cognizant_agency",
        "oversight_agency",
        "oversight_agency",
        "submission_status",
    ]
    readonly_fields = ("submitted_by",)
    search_fields = ("general_information__auditee_uei", "report_id")


class AccessAdmin(admin.ModelAdmin):
    """
    Fields we want in the admin view for Access; we're not showing user here because
    it's redundant with email in almost all circumstances.
    """

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = ("sac", "role", "email")
    list_filter = ["role"]
    readonly_fields = ("sac", "user")
    search_fields = ("email", "sac__report_id")


class DeletedAccessAdmin(admin.ModelAdmin):
    """
    Fields we want in the admin view for DeletedAccess; we're not showing user here
    because it's redundant with email in almost all circumstances.
    """

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = ("sac", "role", "email")
    list_filter = ["role"]
    readonly_fields = ("sac",)
    search_fields = ("email", "removed_by_email", "sac__report_id")


class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "date_created")


class AuditReportAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "date_created", "component_page_numbers")


class SubmissionEventAdmin(admin.ModelAdmin):
    list_display = ("sac", "user", "timestamp", "event")
    search_fields = ("sac__report_id", "user__username")


admin.site.register(Access, AccessAdmin)
admin.site.register(DeletedAccess, DeletedAccessAdmin)
admin.site.register(ExcelFile, ExcelFileAdmin)
admin.site.register(SingleAuditChecklist, SACAdmin)
admin.site.register(SingleAuditReportFile, AuditReportAdmin)
admin.site.register(SubmissionEvent, SubmissionEventAdmin)
