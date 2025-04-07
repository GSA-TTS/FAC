import logging

from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import render
from django.views import View
from django.contrib import messages

from audit.cross_validation.audit_validation_shape import audit_validation_shape
from audit.cross_validation.submission_progress_check import section_completed_metadata
from audit.mixins import SingleAuditChecklistAccessRequiredMixin

from audit.models import (
    Access,
    Audit,
    ExcelFile,
)

from audit.utils import Util
from report_submission.views.utils import create_upload_context, create_delete_context

logger = logging.getLogger(__name__)


class UploadPageView(SingleAuditChecklistAccessRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

        path_name = request.path.split("/")[2]
        additional_context = create_upload_context(report_id)
        context = {
            "auditee_name": audit.auditee_name,
            "report_id": report_id,
            "auditee_uei": audit.auditee_uei,
            "user_provided_organization_type": audit.organization_type,
        }

        for item in additional_context[path_name]:
            context[item] = additional_context[path_name][item]

        context["already_submitted"] = audit.audit.get(
            additional_context[path_name]["DB_id"], None
        )

        shaped_audit = audit_validation_shape(audit)

        completed_metadata = section_completed_metadata(shaped_audit, path_name)

        context["last_uploaded_by"] = completed_metadata[0]
        context["last_uploaded_at"] = completed_metadata[1]

        return render(request, "report_submission/upload-page.html", context)

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            return Util.validate_redirect_url(
                "/audit/submission-progress/{report_id}".format(report_id=report_id)
            )

        except Exception as e:
            logger.info("Unexpected error in UploadPageView post.\n", e)

        raise BadRequest()


class DeleteFileView(SingleAuditChecklistAccessRequiredMixin, View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.additional_context = create_delete_context()

    def get(self, request, *args, **kwargs):

        report_id = kwargs["report_id"]

        try:
            Audit.objects.get(report_id=report_id)

            # Context for every upload page
            context = {
                "report_id": report_id,
            }
            # Using the current URL, append page specific context
            path_name = request.path.split("/")[2]

            context["view_id"] = self.additional_context[path_name]["view_id"]
            context["section_name"] = self.additional_context[path_name]["section_name"]

            return render(request, "report_submission/delete-file-page.html", context)
        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        path_name = request.path.split("/")[2]
        section = self.additional_context[path_name]
        redirect_uri = f"/report_submission/{section['view_id']}/{report_id}"
        try:
            audit = Audit.objects.get(report_id=report_id)
            accesses = Access.objects.filter(audit=audit, user=request.user)

            if not accesses:
                messages.error(request, "You do not have access to this audit.")
                return Util.validate_redirect_url(redirect_uri)

            try:
                excel_files = ExcelFile.objects.filter(
                    audit=audit, form_section=section["form_section"]
                )
                logger.info(f"Deleting {excel_files.count()} files.")
                excel_files.delete()

                del audit.audit[section["field_name"]]
                audit.save(
                    event_type=section["event_type"],
                    event_user=request.user,
                )

            except ExcelFile.DoesNotExist:
                messages.error(request, "File not found.")
                return Util.validate_redirect_url(redirect_uri)

            logger.info("The file has been successfully deleted.")
            return Util.validate_redirect_url(f"/audit/submission-progress/{report_id}")

        except Audit.DoesNotExist:
            logger.error(f"Audit: {report_id} not found")
            messages.error(request, "Audit not found.")
            return Util.validate_redirect_url(redirect_uri)

        except Exception as e:
            logger.error(f"Unexpected error in DeleteFileView post: {str(e)}")
            messages.error(request, "An unexpected error occurred.")
            return Util.validate_redirect_url(redirect_uri)
