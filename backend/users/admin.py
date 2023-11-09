from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html

from .models import Permission, StaffUser, StaffUserLog, UserPermission, UserProfile

User = get_user_model()

admin.site.register(UserProfile)
admin.site.unregister(User)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["slug", "description"]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "can_read_tribal", "last_login", "date_joined"]
    exclude = ["groups", "user_permissions", "password"]
    readonly_fields = ["date_joined", "last_login"]

    def can_read_tribal(self, obj):
        return UserPermission.objects.filter(user=obj, permission__slug="read-tribal").count() > 0

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ["user_link", "permission"]

    def user_link(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.user_id])
        return format_html("<a href='{}'>{}</a>", link, obj.user.email)
    user_link.short_description = "User"


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
