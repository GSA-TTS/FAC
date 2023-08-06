from django.contrib import admin

from audit.models import SingleAuditChecklist, Access, ExcelFile, SingleAuditReportFile


class SACAdmin(admin.ModelAdmin):
    list_display = ("id",)


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
    list_display = (
        "filename",
        "user",
        "date_created",
        "component_page_numbers",
        "user_id",
        "sac",
        "sac_id",
        "file",
    )


admin.site.register(Access, AccessAdmin)
admin.site.register(ExcelFile, ExcelFileAdmin)
admin.site.register(SingleAuditChecklist, SACAdmin)
admin.site.register(SingleAuditReportFile, AuditReportAdmin)
