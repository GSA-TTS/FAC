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
    list_display = ("sac", "role", "email", "user_id")
    list_filter = ("sac", "role")


admin.site.register(Access, AccessAdmin)
admin.site.register(SingleAuditChecklist, SACAdmin)
