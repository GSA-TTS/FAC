from django.contrib import admin

from audit.models import SingleAuditChecklist


class SACAdmin(admin.ModelAdmin):
    list_display = ('id', 'uei', 'auditee_name', 'auditee_fiscal_period_end')
    list_filter = ('auditee_fiscal_period_end', 'auditee_name', 'auditee_state')


admin.site.register(SingleAuditChecklist, SACAdmin)
