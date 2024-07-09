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
from audit.validators import (
    validate_auditee_certification_json,
    validate_auditor_certification_json,
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
    )
    list_filter = [
        "cognizant_agency",
        "oversight_agency",
        "oversight_agency",
        "submission_status",
    ]
    readonly_fields = ("submitted_by",)
    search_fields = ("general_information__auditee_uei", "report_id")


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


class SacValidationWaiverAdmin(admin.ModelAdmin):
    form = SacValidationWaiverForm
    list_display = (
        "report_id",
        "timestamp",
        "approver_email",
        "requester_email",
    )
    list_filter = ("timestamp", "waiver_types")
    search_fields = (
        "report_id__report_id",
        "approver_email",
        "requester_email",
    )
    autocomplete_fields = ["report_id"]

    def save_model(self, request, obj, form, change):
        try:
            sac = SingleAuditChecklist.objects.get(report_id=obj.report_id_id)
            if sac.submission_status in [
                SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION,
                SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED,
            ]:
                self.handle_auditor_certification(request, obj, sac)
                self.handle_auditee_certification(request, obj, sac)
            else:
                messages.set_level(request, messages.WARNING)
                messages.warning(
                    request,
                    f"Cannot apply waiver to SAC with status {sac.submission_status}. Expected status to be one of {SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION}, {SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED}",
                )

            super().save_model(request, obj, form, change)

        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, str(e))

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
            if (
                sac.submission_status
                == SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION
            ):
                validated = validate_auditor_certification_json(auditor_certification)
                sac.auditor_certification = validated
                sac.transition_to_auditor_certified()
                sac.save(
                    event_user=request.user,
                    event_type=SubmissionEvent.EventType.AUDITOR_CERTIFICATION_COMPLETED,
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
            if sac.submission_status == SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED:
                validated = validate_auditee_certification_json(auditee_certification)
                sac.auditee_certification = validated
                sac.transition_to_auditee_certified()
                sac.save(
                    event_user=request.user,
                    event_type=SubmissionEvent.EventType.AUDITEE_CERTIFICATION_COMPLETED,
                )


class UeiValidationWaiverAdmin(admin.ModelAdmin):
    form = UeiValidationWaiverForm
    list_display = (
        "id",
        "uei",
        "timestamp",
        "approver_email",
        "requester_email",
    )
    search_fields = (
        "id",
        "uei",
        "approver_email",
        "requester_email",
    )
    readonly_fields = ('timestamp',)


admin.site.register(Access, AccessAdmin)
admin.site.register(DeletedAccess, DeletedAccessAdmin)
admin.site.register(ExcelFile, ExcelFileAdmin)
admin.site.register(SingleAuditChecklist, SACAdmin)
admin.site.register(SingleAuditReportFile, AuditReportAdmin)
admin.site.register(SubmissionEvent, SubmissionEventAdmin)
admin.site.register(SacValidationWaiver, SacValidationWaiverAdmin)
admin.site.register(UeiValidationWaiver, UeiValidationWaiverAdmin)
