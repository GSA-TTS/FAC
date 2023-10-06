from django.contrib import admin

from .models import StaffUserLog, UserProfile, StaffUser

admin.site.register(UserProfile)


@admin.register(StaffUserLog)
class StaffUserLogAdmin(admin.ModelAdmin):
    list_display = [
        "staff_email",
        "added_by_email",
        "date_added",
        "removed_by_email",
        "date_removed",
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StaffUser)
class StaffUserAdmin(admin.ModelAdmin):
    list_display = [
        "staff_email",
        "added_by_email",
        "date_added",
    ]
    fields = [
        "staff_email",
    ]

    def save_model(self, request, obj, form, change):
        obj.added_by_email = request.user.email
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        StaffUserLog(
            staff_email=obj.staff_email,
            added_by_email=obj.added_by_email,
            date_added=obj.date_added,
            removed_by_email=request.user.email,
        ).save()
        super().delete_model(request, obj)

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return False
