import logging
from django.conf import settings
from django.contrib import admin, messages
from audit.forms import SacValidationWaiverForm, UeiValidationWaiverForm
from audit.models import (
    Access,
    DeletedAccess,
    ExcelFile,
    SingleAuditChecklist,
    SingleAuditReportFile,
    SubmissionEvent,
    SacValidationWaiver,
    UeiValidationWaiver,
)
from audit.models.models import STATUS
from audit.models.viewflow import (
    sac_flag_for_removal,
    sac_revert_from_flagged_for_removal,
    sac_transition,
)
from audit.validators import (
    validate_auditee_certification_json,
    validate_auditor_certification_json,
)
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@admin.action(description="Revert selected report(s) to In Progress")
def revert_to_in_progress(modeladmin, request, queryset):
    successful_reverts = []
    errors = []

    for sac in queryset:
        if sac.submission_status == STATUS.FLAGGED_FOR_REMOVAL:
            try:
                sac_revert_from_flagged_for_removal(sac, request.user)
                sac.save()
                successful_reverts.append(sac.report_id)
            except Exception as e:
                modeladmin.message_user(
                    request,
                    f"Error reverting {sac.report_id}: {str(e)}",
                    level=messages.ERROR,
                )
                errors.append(sac.report_id)
        else:
            modeladmin.message_user(
                request,
                f"Report {sac.report_id} is not flagged for removal.",
                level=messages.WARNING,
            )
            errors.append(sac.report_id)

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
def flag_for_removal(modeladmin, request, queryset):

    flagged = []
    already_flagged = []

    for sac in queryset:
        if sac.submission_status != STATUS.FLAGGED_FOR_REMOVAL:
            sac_flag_for_removal(sac, request.user)
            sac.save()
            flagged.append(sac.report_id)
        else:
            already_flagged.append(sac.report_id)

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


class SACAdmin(admin.ModelAdmin):
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
    search_fields = ("general_information__auditee_uei", "report_id")
    actions = [revert_to_in_progress, flag_for_removal]


class AccessAdmin(admin.ModelAdmin):
    """
    Fields we want in the admin view for Access; we're not showing user here because
    it's redundant with email in almost all circumstances.
    """

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = ("sac", "role", "email")
    list_filter = ["role"]
    readonly_fields = ("sac", "user")
    search_fields = ("email", "sac__report_id")


class DeletedAccessAdmin(admin.ModelAdmin):
    """
    Fields we want in the admin view for DeletedAccess; we're not showing user here
    because it's redundant with email in almost all circumstances.
    """

    def has_module_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    list_display = ("sac", "role", "email")
    list_filter = ["role"]
    readonly_fields = ("sac",)
    search_fields = ("email", "removed_by_email", "sac__report_id")


class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "date_created")


class AuditReportAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "date_created", "component_page_numbers")


class SubmissionEventAdmin(admin.ModelAdmin):
    list_display = ("sac", "user", "timestamp", "event")
    search_fields = ("sac__report_id", "user__username")


class WaiverTypesFilter(SimpleListFilter):
    title = _("Waiver Types")
    parameter_name = "waiver_types"

    def lookups(self, request, model_admin):
        waiver_types = set(
            [
                waiver_type
                for waiver in SacValidationWaiver.objects.all()
                for waiver_type in waiver.waiver_types
            ]
        )
        return [(waiver_type, waiver_type) for waiver_type in waiver_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(waiver_types__contains=[self.value()])
        return queryset


class SacValidationWaiverAdmin(admin.ModelAdmin):
    form = SacValidationWaiverForm
    list_display = (
        "report_id",
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
        try:
            sac = SingleAuditChecklist.objects.get(report_id=obj.report_id_id)
            if sac.submission_status in [
                STATUS.READY_FOR_CERTIFICATION,
                STATUS.AUDITOR_CERTIFIED,
            ]:
                logger.info(
                    f"User {request.user.email} is applying waiver for SAC with status: {sac.submission_status}"
                )
                self.handle_auditor_certification(request, obj, sac)
                self.handle_auditee_certification(request, obj, sac)
                super().save_model(request, obj, form, change)
                logger.info(
                    f"SAC {sac.report_id} updated successfully with waiver by user: {request.user.email}."
                )
            elif (
                STATUS.IN_PROGRESS
                and SacValidationWaiver.TYPES.FINDING_REFERENCE_NUMBER
                in obj.waiver_types
            ):
                logger.info(
                    f"User {request.user.email} is applying waiver for SAC with status: {sac.submission_status}"
                )
                super().save_model(request, obj, form, change)
                logger.info(
                    f"Duplicate finding reference number waiver applied to SAC {sac.report_id} by user: {request.user.email}."
                )
            elif (
                STATUS.IN_PROGRESS
                and SacValidationWaiver.TYPES.PRIOR_REFERENCES in obj.waiver_types
            ):
                logger.info(
                    f"User {request.user.email} is applying waiver for SAC with status: {sac.submission_status}"
                )
                super().save_model(request, obj, form, change)
                logger.info(
                    f"Invalid prior reference waiver applied to SAC {sac.report_id} by user: {request.user.email}."
                )
            else:
                messages.set_level(request, messages.WARNING)
                messages.warning(
                    request,
                    f"Cannot apply waiver to SAC with status {sac.submission_status}. Expected status to be one of {STATUS.READY_FOR_CERTIFICATION}, {STATUS.AUDITOR_CERTIFIED}, or {STATUS.IN_PROGRESS}.",
                )
                logger.warning(
                    f"User {request.user.email} attempted to apply waiver to SAC with invalid status: {sac.submission_status}"
                )

        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, str(e))
            logger.error(
                f"Error saving SAC waiver by user {request.user.email}: {str(e)}",
                exc_info=True,
            )

    def handle_auditor_certification(self, request, obj, sac):
        if SacValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL in obj.waiver_types:
            auditor_certification = sac.auditor_certification or {}
            auditor_certification.update(
                {
                    "auditor_certification": {
                        "is_OMB_limited": True,
                        "is_auditee_responsible": True,
                        "has_used_auditors_report": True,
                        "has_no_auditee_procedures": True,
                        "is_accurate_and_complete": True,
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
            if sac.submission_status == STATUS.READY_FOR_CERTIFICATION:
                validated = validate_auditor_certification_json(auditor_certification)
                sac.auditor_certification = validated
                if sac_transition(request, sac, transition_to=STATUS.AUDITOR_CERTIFIED):
                    logger.info(
                        f"Auditor certification completed for SAC {sac.report_id} by user: {request.user.email}."
                    )

    def handle_auditee_certification(self, request, obj, sac):
        if SacValidationWaiver.TYPES.AUDITEE_CERTIFYING_OFFICIAL in obj.waiver_types:
            auditee_certification = sac.auditee_certification or {}
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
            if sac.submission_status == STATUS.AUDITOR_CERTIFIED:
                validated = validate_auditee_certification_json(auditee_certification)
                sac.auditee_certification = validated

                if sac_transition(request, sac, transition_to=STATUS.AUDITEE_CERTIFIED):
                    logger.info(
                        f"Auditee certification completed for SAC {sac.report_id} by user: {request.user.email}."
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
admin.site.register(SingleAuditChecklist, SACAdmin)
admin.site.register(SingleAuditReportFile, AuditReportAdmin)
admin.site.register(SubmissionEvent, SubmissionEventAdmin)
admin.site.register(SacValidationWaiver, SacValidationWaiverAdmin)
admin.site.register(UeiValidationWaiver, UeiValidationWaiverAdmin)
