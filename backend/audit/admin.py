from django.contrib import admin

from audit.models import SingleAuditChecklist, Access


class SACAdmin(admin.ModelAdmin):
    list_display = ("id", "auditee_uei", "auditee_name", "auditee_fiscal_period_end")
    list_filter = (
        "auditee_fiscal_period_end",
        "auditee_name",
        "auditee_state",
    )


class AccessAdmin(admin.ModelAdmin):
    list_display = ("role", "email", "user")
    list_filter = ["role"]


admin.site.register(Access, AccessAdmin)
admin.site.register(SingleAuditChecklist, SACAdmin)
