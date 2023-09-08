from django.contrib import admin

from .models import CognizantBaseline, CognizantAssignment


class CognizantBaselineAdmin(admin.ModelAdmin):
    date_hierarchy = "date_assigned"
    ordering = ["date_assigned"]
    empty_value_display = "-empty-"


class CognizantAssignmentAdmin(admin.ModelAdmin):
    date_hierarchy = "date_assigned"
    ordering = ["date_assigned"]
    empty_value_display = "-empty-"


admin.site.register(CognizantBaseline, CognizantBaselineAdmin)
admin.site.register(CognizantAssignment, CognizantAssignmentAdmin)
