from django.contrib import admin

from .models import CognizantBaseline


class CognizantBaselineAdmin(admin.ModelAdmin):
    date_hierarchy = "date_assigned"


admin.site.register(CognizantBaseline, CognizantBaselineAdmin)
