from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from audit.models import SingleAuditChecklist
from dissemination.models import TribalApiAccessKeyIds
from users.models import UserPermission
from .models import CognizantAssignment, AssignmentTypeCode

import json
from datetime import date


class DateEncoder(json.JSONEncoder):
    """Encode date types in admin logs."""

    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


class SupportAdmin(admin.ModelAdmin):
    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CognizantAssignment)
class CognizantAssignmentAdmin(SupportAdmin):
    date_hierarchy = "date_assigned"
    ordering = ["date_assigned"]
    list_display = [
        "report_id",
        "uei",
        "cognizant_agency",
        "date_assigned",
        "assignor_email",
        "override_comment",
        "assignment_type",
    ]
    list_filter = [
        "assignment_type",
        "cognizant_agency",
    ]
    fields = [
        "report_id",
        (
            "uei",
            "last_assigned_by",
            "current_cog",
        ),
        "cognizant_agency",
        "override_comment",
    ]
    readonly_fields = [
        "uei",
        "last_assigned_by",
        "current_cog",
    ]

    def uei(self, obj):
        return SingleAuditChecklist.objects.get(report_id=obj.report_id).auditee_uei

    def current_cog(self, obj):
        return SingleAuditChecklist.objects.get(
            report_id=obj.report_id
        ).cognizant_agency

    def last_assigned_by(self, obj):
        return obj.assignor_email

    save_as = True
    save_as_continue = False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """customize edit form"""
        extra_context = extra_context or {}
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = False
        extra_context["show_save_and_add_another"] = (
            False  # this does not work if has_add_permision is True
        )
        return super().change_view(request, object_id, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        obj.assignor_email = request.user.email
        obj.assignment_type = AssignmentTypeCode.MANUAL
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff


@admin.register(LogEntry)
class LogEntryAdmin(SupportAdmin):
    """
    Displays the changelog for actions made from the Admin Panel.
    """

    date_hierarchy = "action_time"
    ordering = ["-action_time"]
    list_display = [
        "action_time",
        "staff_user",
        "record_affected",
        "event",
        "content",
    ]
    search_fields = (
        "action_time",
        "user__email",
        "object_repr",
        "action_flag",
        "change_message",
    )

    def staff_user(self, obj):
        """The staffuser."""
        return obj.user.email

    def record_affected(self, obj):
        """The record associated with the staffuser's action."""
        return obj.object_repr

    def event(self, obj):
        """Shares the action taken by the staffuser."""

        if obj.action_flag == ADDITION:
            return "Created"
        elif obj.action_flag == DELETION:
            return "Deleted"
        elif obj.action_flag == CHANGE:
            res = "Updated"
            if obj.change_message:
                _json = json.loads(obj.change_message)

                # The LogEntry has recorded changes.
                if _json:
                    _json = _json[0]
                    if "changed" in _json:
                        res = "Updated\n"
                        for field in _json["changed"]["fields"]:
                            res += f"\n- {field}"

                # No changes were actually made.
                else:
                    res += "\n- No changes"
            return res
        return "-"

    def content(self, obj):
        """The raw contents of the record that was changed."""

        if obj.change_message:
            _json = json.loads(obj.change_message)

            # The LogEntry has recorded changes.
            if _json:
                _json = _json[0]
                if "content" in _json:
                    return _json["content"]

            # No changes were actually made.
            else:
                return "No changes"

        return "-"


@receiver([post_delete, post_save], sender=LogEntry)
def add_custom_field_to_log(sender, instance, created, **kwargs):
    """
    Modify content of the log depending on what model(s) were changed.
    """

    if created:
        model_class = instance.content_type.model_class()
        qset = model_class.objects.filter(pk=instance.object_id)
        if qset.exists():
            obj = qset.first()

        # update content of record after save occurred.
        change_message_json = json.loads(instance.change_message)

        if change_message_json:
            if model_class == UserPermission:
                change_message_json[0]["content"] = list(
                    qset.values("email", "permission__slug")
                )
            elif model_class == TribalApiAccessKeyIds:
                change_message_json[0]["content"] = list(qset.values("email", "key_id"))
            else:
                change_message_json[0]["content"] = list(qset.values("id"))

            # record still exists.
            if obj:
                change_message_json[0]["id"] = obj.pk

        # write changes to instance.
        instance.change_message = json.dumps(change_message_json, cls=DateEncoder)
        instance.save()
