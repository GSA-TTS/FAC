from django.contrib import admin

from audit.models import SingleAuditChecklist, Access, ExcelFile, SingleAuditReportFile


class SACAdmin(admin.ModelAdmin):
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
    ]

    fields = (
        "report_id",
        (
            "cognizant_agency",
            "oversight_agency",
        ),
        "general_information",
    )


class AccessAdmin(admin.ModelAdmin):
    """
    Fields we want in the admin view for Access; we're not showing user here because
    it's redundant with email in almost all circumstances.
    """

    list_display = ("sac", "role", "email")
    list_filter = ["role"]


class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "date_created")


class AuditReportAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "date_created", "component_page_numbers")


admin.site.register(Access, AccessAdmin)
admin.site.register(ExcelFile, ExcelFileAdmin)
admin.site.register(SingleAuditChecklist, SACAdmin)
admin.site.register(SingleAuditReportFile, AuditReportAdmin)
