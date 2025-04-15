import datetime
import logging
from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse
from audit.forms import (
    AuditValidationWaiverForm,
    UeiValidationWaiverForm,
)
from audit.models import (
    Access,
    Audit,
    DeletedAccess,
    ExcelFile,
    History,
    SingleAuditReportFile,
    AuditValidationWaiver,
    UeiValidationWaiver,
)
from audit.models.constants import STATUS, EventType
from audit.models.viewflow import (
    audit_flag_for_removal,
    audit_revert_from_flagged_for_removal,
    audit_transition,
)
from audit.validators import (
    validate_auditee_certification_json,
    validate_auditor_certification_json,
)
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.utils.timezone import now

from dissemination.remove_singleauditreport_pdf import (
    audit_remove_singleauditreport_pdf,
)
from dissemination.remove_workbook_artifacts import (
    audit_remove_workbook_artifacts,
)

logger = logging.getLogger(__name__)

# As per ADR #0041, the retention period for flagged reports is 6 months. That is 180 days.
FLAGGED_REPORT_RETENTION_DAYS = 180  # 6 months


def admin_message(request, message_type, ui_message, logger_message=None):
    """Return a message to the user in the Django admin UI. (and optionally send a log)."""
    messages.set_level(request, message_type)

    if message_type == messages.INFO:
        messages.info(request, ui_message)
        if logger_message:
            logger.info(logger_message)
    if message_type == messages.WARNING:
        messages.warning(request, ui_message)
        if logger_message:
            logger.warning(logger_message)
    if message_type == messages.ERROR:
        messages.error(request, ui_message)
        if logger_message:
            logger.error(logger_message)


@admin.action(description="Delete reports flagged for removal for over 6 months")
def audit_delete_flagged_records(modeladmin, request, queryset):
    """
    Admin action to delete records flagged for removal older than the specified months.
    """
    cutoff_date = now() - datetime.timedelta(days=FLAGGED_REPORT_RETENTION_DAYS)
    count = 0
    failed_count = 0
    report_ids = []
    failed_report_ids = []

    # Filter records for deletion.
    records_to_delete = queryset.filter(
        submission_status=STATUS.FLAGGED_FOR_REMOVAL, updated_at__lte=cutoff_date
    )

    for audit in records_to_delete:

        try:

            # Delete the record and all its associated data.
            with transaction.atomic():
                auditee_uei = audit.audit.get("general_information", {}).get(
                    "auditee_uei"
                )
                if auditee_uei:
                    UeiValidationWaiver.objects.filter(uei=auditee_uei).delete()
                AuditValidationWaiver.objects.filter(report_id=audit).delete()
                audit_remove_singleauditreport_pdf(audit)
                audit_remove_workbook_artifacts(audit)
                Access.objects.filter(audit=audit).delete()
                DeletedAccess.objects.filter(audit=audit).delete()
                History.objects.filter(report_id=audit.report_id).delete()
                ExcelFile.objects.filter(audit=audit).delete()
                SingleAuditReportFile.objects.filter(audit=audit).delete()
                report_ids.append(audit.report_id)
                audit.delete()
                count += 1

        except Exception as e:
            logger.error(
                f"Failed to delete audit report with ID {audit.report_id}: {str(e)}"
            )
            failed_count += 1
            failed_report_ids.append(audit.report_id)
            continue

    if count:
        logger.info(
            f"Deleted {count} flagged records and their associated child records. Report IDs: {', '.join(report_ids)}"
        )
        modeladmin.message_user(
            request,
            f"Successfully deleted {count} flagged records and their associated child records. Report IDs: {', '.join(report_ids)}",
        )
    if failed_count:
        logger.error(
            f"Failed to delete {failed_count} flagged records. Report IDs: {', '.join(failed_report_ids)}"
        )
        modeladmin.message_user(
            request,
            f"Failed to delete {failed_count} flagged records. Report IDs: {', '.join(failed_report_ids)}",
            level=messages.ERROR,
        )


@admin.action(description="Revert selected report(s) to In Progress")
def audit_revert_to_in_progress(modeladmin, request, queryset):
    successful_reverts = []
    errors = []

    for audit in queryset:
        if audit.submission_status == STATUS.FLAGGED_FOR_REMOVAL:
            try:
                audit_revert_from_flagged_for_removal(audit, request.user)
                audit.save()
                successful_reverts.append(audit.report_id)
            except Exception as e:
                modeladmin.message_user(
                    request,
                    f"Error reverting {audit.report_id}: {str(e)}",
                    level=messages.ERROR,
                )
                errors.append(audit.report_id)
        else:
            modeladmin.message_user(
                request,
                f"Report {audit.report_id} is not flagged for removal.",
                level=messages.WARNING,
            )
            errors.append(audit.report_id)

    if successful_reverts:
        modeladmin.message_user(
            request,
            f"Successfully reverted report(s) ({', '.join(successful_reverts)}) back to In Progress.",
            level=messages.SUCCESS,
        )

    if errors:
        modeladmin.message_user(
            request,
            f"Unable to revert report(s) ({', '.join(errors)}) back to In Progress.",
            level=messages.ERROR,
        )


@admin.action(description="Flag selected report(s) for removal")
def flag_audit_for_removal(modeladmin, request, queryset):

    flagged = []
    already_flagged = []

    for audit in queryset:
        if audit.submission_status != STATUS.FLAGGED_FOR_REMOVAL:
            audit_flag_for_removal(audit, request.user)
            audit.save()
            flagged.append(audit.report_id)
        else:
            already_flagged.append(audit.report_id)

    if flagged:
        modeladmin.message_user(
            request,
            f"Successfully flagged report(s) ({', '.join(flagged)}) for removal.",
            level=messages.SUCCESS,
        )

    if already_flagged:
        modeladmin.message_user(
            request,
            f"Report(s) ({', '.join(already_flagged)}) were already flagged.",
            level=messages.WARNING,
        )


class AuditAdmin(admin.ModelAdmin):
    """
    Support for read-only staff access, and control of what fields are present and
    filterable/searchable.
    """

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "id",
        "report_id",
        "cognizant_agency",
        "oversight_agency",
        "submission_status",
    )
    list_filter = [
        "cognizant_agency",
        "oversight_agency",
        "oversight_agency",
        "submission_status",
    ]
    readonly_fields = ("submitted_by",)
    search_fields = ("audit__general_information__auditee_uei", "report_id")
    actions = [
        audit_revert_to_in_progress,
        flag_audit_for_removal,
        audit_delete_flagged_records,
    ]

    def changelist_view(self, request, extra_context=None):
        """
        Override changelist_view to allow running the action without selection.
        """
        if (
            "action" in request.POST
            and request.POST["action"] == "delete_flagged_records"
        ):
            queryset = self.get_queryset(request)
            audit_delete_flagged_records(self, request, queryset)
            # Redirect to avoid Django's "No items selected" error and ensure a valid response
            return redirect(
                reverse(
                    f"admin:{self.opts.app_label}_{self.opts.model_name}_changelist"
                )
            )

        return super().changelist_view(request, extra_context=extra_context)


class AuditHistoryAdmin(admin.ModelAdmin):
    """
    Support for read-only staff access, and control of what fields are present and
    filterable/searchable.
    """

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = (
        "id",
        "report_id",
        "updated_at",
        "event_display",
        "updated_by__email",
        "version",
    )
    list_filter = [
        "report_id",
        "updated_at",
        "event",
        "updated_by__email",
        "version",
    ]
    search_fields = ("report_id", "updated_by__email")
    ordering = ("-updated_at",)

    def event_display(self, obj):
        return obj.get_event_display()

    event_display.admin_order_field = "event"  # type: ignore
    event_display.short_description = _("Event")  # type: ignore


class AccessAdmin(admin.ModelAdmin):
    """
    Fields we want in the admin view for Access; we're not showing user here because
    it's redundant with email in almost all circumstances.
    """

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = ("audit", "role", "email")
    list_filter = ["role"]
    readonly_fields = ("audit", "user")
    search_fields = ("email", "audit__report_id")


class DeletedAccessAdmin(admin.ModelAdmin):
    """
    Fields we want in the admin view for DeletedAccess; we're not showing user here
    because it's redundant with email in almost all circumstances.
    """

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = ("audit", "role", "email")
    list_filter = ["role"]
    readonly_fields = ("audit",)
    search_fields = ("email", "removed_by_email", "audit__report_id")


class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "date_created")


class AuditReportAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "date_created", "component_page_numbers")


class WaiverTypesFilter(SimpleListFilter):
    title = _("Waiver Types")
    parameter_name = "waiver_types"

    def lookups(self, request, model_admin):
        waiver_types = set(
            [
                waiver_type
                for waiver in AuditValidationWaiver.objects.all()
                for waiver_type in waiver.waiver_types
            ]
        )
        return [(waiver_type, waiver_type) for waiver_type in waiver_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(waiver_types__contains=[self.value()])
        return queryset


class AuditValidationWaiverAdmin(admin.ModelAdmin):
    form = AuditValidationWaiverForm
    list_display = (
        "report_by_id",
        "timestamp",
        "approver_email",
        "requester_email",
    )
    list_filter = ("timestamp", WaiverTypesFilter)
    search_fields = (
        "report_id__report_id",
        "approver_email",
        "requester_email",
    )
    autocomplete_fields = ["report_id"]

    def report_by_id(self, obj):
        return obj.report_id.report_id

    def save_model(self, request, obj, form, change):
        try:
            audit = Audit.objects.get(report_id=obj.report_id_id)

            # Creating a waiver for an audit in the certification process (before auditee_certified).
            if audit.submission_status in [
                STATUS.READY_FOR_CERTIFICATION,
                STATUS.AUDITOR_CERTIFIED,
            ]:
                self.handle_auditor_certification(request, obj, audit)
                self.handle_auditee_certification(request, obj, audit)
                super().save_model(request, obj, form, change)
                admin_message(
                    request,
                    messages.INFO,
                    f"Audit {audit.report_id} updated successfully with waiver by user: {request.user.email}.",
                    f"User {request.user.email} is applying waiver for Audit with status: {audit.submission_status}",
                )

            # Creating a waiver for an in_progress audit.
            elif STATUS.IN_PROGRESS:

                # Audit does not have the appropriate waiver type for its in_progress status.
                if (
                    AuditValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL
                    in obj.waiver_types
                    or AuditValidationWaiver.TYPES.AUDITEE_CERTIFYING_OFFICIAL
                    in obj.waiver_types
                ):
                    admin_message(
                        request,
                        messages.WARNING,
                        f"Cannot apply waiver to Audit with status {audit.submission_status}. {obj.waiver_types} is an invalid type of waiver for this Audit.",
                        f"User {request.user.email} attempted to apply waiver to Audit with invalid status: {audit.submission_status}",
                    )

                else:

                    # Create the waiver - audit submission now ignores duplicate finding reference numbers.
                    if (
                        AuditValidationWaiver.TYPES.FINDING_REFERENCE_NUMBER
                        in obj.waiver_types
                    ):
                        super().save_model(request, obj, form, change)
                        admin_message(
                            request,
                            messages.INFO,
                            f"Duplicate finding reference number waiver applied to Audit {audit.report_id} by user: {request.user.email}.",
                            f"User {request.user.email} is applying waiver for Audit with status: {audit.submission_status}",
                        )

                    # Create the waiver - audit submission now ignores invalid prior references.
                    elif (
                        AuditValidationWaiver.TYPES.PRIOR_REFERENCES in obj.waiver_types
                    ):
                        super().save_model(request, obj, form, change)
                        admin_message(
                            request,
                            messages.INFO,
                            f"Invalid prior reference waiver applied to Audit {audit.report_id} by user: {request.user.email}.",
                            f"User {request.user.email} is applying waiver for Audit with status: {audit.submission_status}",
                        )

                    # Audit does not have the appropriate waiver type for its in_progress status.
                    else:
                        admin_message(
                            request,
                            messages.WARNING,
                            f"Cannot apply waiver to Audit with status {audit.submission_status}. Expected status to be one of {STATUS.READY_FOR_CERTIFICATION}, {STATUS.AUDITOR_CERTIFIED}, or {STATUS.IN_PROGRESS}.",
                            f"User {request.user.email} attempted to apply waiver to Audit with invalid status: {audit.submission_status}",
                        )

            # Cannot create waiver since the audit status is invalid.
            else:
                admin_message(
                    request,
                    messages.WARNING,
                    f"Cannot apply waiver to Audit with status {audit.submission_status}. Expected status to be one of {STATUS.READY_FOR_CERTIFICATION}, {STATUS.AUDITOR_CERTIFIED}, or {STATUS.IN_PROGRESS}.",
                    f"User {request.user.email} attempted to apply waiver to Audit with invalid status: {audit.submission_status}",
                )

        except Exception as e:
            admin_message(
                request,
                messages.ERROR,
                str(e),
                f"Error saving Audit waiver by user {request.user.email}: {str(e)}",
            )

    def handle_auditor_certification(self, request, obj, audit):
        if AuditValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL in obj.waiver_types:
            auditor_certification = audit.audit.get("auditor_certification", {})
            auditor_certification.update(
                {
                    "auditor_certification": {
                        "is_OMB_limited": True,
                        "is_auditee_responsible": True,
                        "has_used_auditors_report": True,
                        "has_no_auditee_procedures": True,
                        "is_FAC_releasable": True,
                    },
                    "auditor_signature": {
                        "auditor_name": settings.GSA_FAC_WAIVER,
                        "auditor_title": settings.GSA_FAC_WAIVER,
                        "auditor_certification_date_signed": obj.timestamp.strftime(
                            "%Y-%m-%d"
                        ),
                    },
                }
            )
            if audit.submission_status == STATUS.READY_FOR_CERTIFICATION:
                validated = validate_auditor_certification_json(auditor_certification)
                audit.audit["auditor_certification"] = validated
                if audit_transition(
                    request,
                    audit,
                    event=EventType.AUDITOR_CERTIFICATION_COMPLETED,
                ):
                    logger.info(
                        f"Auditor certification completed for Audit {audit.report_id} by user: {request.user.email}."
                    )

    def handle_auditee_certification(self, request, obj, audit):
        if AuditValidationWaiver.TYPES.AUDITEE_CERTIFYING_OFFICIAL in obj.waiver_types:
            auditee_certification = audit.audit.get("auditee_certification", {})
            auditee_certification.update(
                {
                    "auditee_certification": {
                        "has_no_PII": True,
                        "has_no_BII": True,
                        "meets_2CFR_specifications": True,
                        "is_2CFR_compliant": True,
                        "is_complete_and_accurate": True,
                        "has_engaged_auditor": True,
                        "is_issued_and_signed": True,
                        "is_FAC_releasable": True,
                    },
                    "auditee_signature": {
                        "auditee_name": settings.GSA_FAC_WAIVER,
                        "auditee_title": settings.GSA_FAC_WAIVER,
                        "auditee_certification_date_signed": obj.timestamp.strftime(
                            "%Y-%m-%d"
                        ),
                    },
                }
            )
            if audit.submission_status == STATUS.AUDITOR_CERTIFIED:
                validated = validate_auditee_certification_json(auditee_certification)
                audit.audit["auditee_certification"] = validated

                if audit_transition(
                    request,
                    audit,
                    event=EventType.AUDITEE_CERTIFICATION_COMPLETED,
                ):
                    logger.info(
                        f"Auditee certification completed for Audit {audit.report_id} by user: {request.user.email}."
                    )


class UeiValidationWaiverAdmin(admin.ModelAdmin):
    form = UeiValidationWaiverForm
    list_display = (
        "id",
        "uei",
        "timestamp",
        "expiration",
        "approver_email",
        "requester_email",
        "justification",
    )
    search_fields = (
        "id",
        "uei",
        "approver_email",
        "requester_email",
    )
    readonly_fields = ("timestamp",)

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(
            f'Validation Waiver for UEI "{obj.uei}" successfully added by user: {request.user.email}.'
        )


admin.site.register(Access, AccessAdmin)
admin.site.register(DeletedAccess, DeletedAccessAdmin)
admin.site.register(ExcelFile, ExcelFileAdmin)
admin.site.register(Audit, AuditAdmin)
admin.site.register(History, AuditHistoryAdmin)
admin.site.register(SingleAuditReportFile, AuditReportAdmin)
admin.site.register(AuditValidationWaiver, AuditValidationWaiverAdmin)
admin.site.register(UeiValidationWaiver, UeiValidationWaiverAdmin)
