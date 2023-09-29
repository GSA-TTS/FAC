from django.contrib import admin

from audit.models import SingleAuditChecklist, Access, ExcelFile


class SACAdmin(admin.ModelAdmin):
    list_display = ("id", "report_id")


class AccessAdmin(admin.ModelAdmin):
    list_display = ("role", "email", "user")
    list_filter = ["role"]


class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "date_created")


admin.site.register(Access, AccessAdmin)
admin.site.register(ExcelFile, ExcelFileAdmin)
admin.site.register(SingleAuditChecklist, SACAdmin)
