from django.contrib import admin

from audit.models import SingleAuditChecklist, Access


class SACAdmin(admin.ModelAdmin):
    list_display = ("id",)


class AccessAdmin(admin.ModelAdmin):
    list_display = ("role", "email", "user")
    list_filter = ["role"]


admin.site.register(Access, AccessAdmin)
admin.site.register(SingleAuditChecklist, SACAdmin)
