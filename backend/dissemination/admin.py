from django.contrib import admin
from dissemination.models import (
    AdditionalEin,
    AdditionalUei,
    CapText,
    FederalAward,
    Finding,
    FindingText,
    General,
    Note,
    Passthrough,
    SecondaryAuditor,
    TribalApiAccessKeyIds,
)
import datetime


class AdditionalEinAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "additional_ein",
    )

    search_fields = ("report_id__report_id", "additional_ein")


class AdditionalUeiAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "additional_uei",
    )

    search_fields = ("report_id__report_id", "additional_uei")


class CapTextAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "finding_ref_number",
    )

    search_fields = ("report_id__report_id", "finding_ref_number")


class FederalAwardAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "award_reference",
    )

    search_fields = (
        "report_id__report_id",
        "award_reference",
    )


class FindingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "award_reference",
        "reference_number",
    )

    search_fields = ("report_id__report_id", "award_reference", "reference_number")


class FindingTextAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "finding_ref_number",
    )

    search_fields = ("report_id__report_id", "finding_ref_number")


class GeneralAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "auditee_name",
        "date_created",
    )

    search_fields = ("report_id", "auditee_name", "date_created")


class NoteAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "note_title",
    )

    search_fields = ("report_id__report_id", "note_title")


class PassThroughAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "award_reference",
        "passthrough_id",
    )

    search_fields = ("report_id__report_id", "award_reference", "passthrough_id")


class SecondaryAuditorAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "report_id",
        "auditor_ein",
    )

    search_fields = ("report_id__report_id", "auditor_ein")


class TribalApiAccessKeyIdsAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "key_id",
        "date_added",
    )

    search_fields = (
        "email",
        "key_id",
    )

    fields = [
        "email",
        "key_id",
    ]

    def save_model(self, request, obj, form, change):
        obj.date_added = datetime.date.today()
        super().save_model(request, obj, form, change)


admin.site.register(AdditionalEin, AdditionalEinAdmin)
admin.site.register(AdditionalUei, AdditionalUeiAdmin)
admin.site.register(CapText, CapTextAdmin)
admin.site.register(FederalAward, FederalAwardAdmin)
admin.site.register(Finding, FindingAdmin)
admin.site.register(FindingText, FindingTextAdmin)
admin.site.register(General, GeneralAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Passthrough, PassThroughAdmin)
admin.site.register(SecondaryAuditor, SecondaryAuditorAdmin)
admin.site.register(TribalApiAccessKeyIds, TribalApiAccessKeyIdsAdmin)
