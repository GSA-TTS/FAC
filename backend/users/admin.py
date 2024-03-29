from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Permission, StaffUser, StaffUserLog, UserPermission, UserProfile
from .permissions import can_read_tribal as _can_read_tribal

User = get_user_model()

admin.site.register(UserProfile)
admin.site.unregister(User)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["slug", "description"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "can_read_tribal", "last_login", "date_joined"]
    list_filter = ["is_staff", "is_superuser"]
    exclude = ["groups", "user_permissions", "password"]
    readonly_fields = ["date_joined", "last_login"]
    search_fields = ("email", "username")

    def can_read_tribal(self, obj):
        return _can_read_tribal(obj)


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ["user", "email", "permission"]
    search_fields = ("email", "permission", "user")


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

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
