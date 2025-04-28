import logging

from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import render
from django.views import View
from django.contrib import messages

from audit.cross_validation import sac_validation_shape
from audit.cross_validation.audit_validation_shape import audit_validation_shape
from audit.cross_validation.submission_progress_check import section_completed_metadata
from audit.mixins import SingleAuditChecklistAccessRequiredMixin

from audit.models import (
    Access,
    SingleAuditChecklist,
    SubmissionEvent,
    Audit,
    ExcelFile,
)

from audit.utils import Util
from report_submission.views.utils import create_upload_context, create_delete_context

logger = logging.getLogger(__name__)


class UploadPageView(SingleAuditChecklistAccessRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        # SOT TODO: Enable for testing
        # if request.GET.get("beta", "N") == "Y":
        #     return _handle_sot_beta_upload_get(request, *args, **kwargs)

        # Organized by URL name, page specific constants are defined here
        # Data can then be accessed by checking the current URL
        additional_context = create_upload_context(report_id)

        try:
            # TODO SOT: Update for `audit`
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # Context for every upload page
            context = {
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
            }
            # Using the current URL, append page specific context
            path_name = request.path.split("/")[2]

            for item in additional_context[path_name]:
                context[item] = additional_context[path_name][item]
            try:
                context["already_submitted"] = getattr(
                    sac, additional_context[path_name]["DB_id"]
                )

                shaped_sac = sac_validation_shape(sac)

                audit = Audit.objects.find_audit_or_none(report_id=report_id)
                if audit:
                    shaped_audit = audit_validation_shape(audit)
                    _compare_shapes(shaped_sac, shaped_audit)
                else:
                    logger.debug("A SOT does not yet exist for this SAC.\n")

                # This tuple can come back as None, None, which is fine.
                uploaded_by, uploaded_at = section_completed_metadata(
                    shaped_sac, path_name
                )

                # SOT TODO: This needs to be changed/improved
                # for the migration to SOT. I think it wants to operate on the
                # shaped_audit, but we don't need it now/here.
                # completed_audit_audit = section_completed_metadata(
                #     shaped_sac, path_name
                # )
                # _compare_completed_metadata(completed_metadata, completed_audit_audit)

                context["last_uploaded_by"] = uploaded_by
                context["last_uploaded_at"] = uploaded_at
            except Exception:
                context["already_submitted"] = None

            return render(request, "report_submission/upload-page.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            return Util.validate_redirect_url(
                "/audit/submission-progress/{report_id}".format(report_id=report_id)
            )
        except Exception as e:
            logger.error("Unexpected error in UploadPageView post.\n", e)

        # FIXME: This feels like a fragile control pathway.
        # At the moment, you should ALWAYS return OR throw an exception.
        # But, the future could change this. Therefore, what happens outside of
        # the `except` could matter.
        raise BadRequest()


class DeleteFileView(SingleAuditChecklistAccessRequiredMixin, View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.additional_context = create_delete_context()

    def get(self, request, *args, **kwargs):

        report_id = kwargs["report_id"]

        try:
            # TODO: Update Post SOC Launch -> don't use sac.
            SingleAuditChecklist.objects.get(report_id=report_id)

            # Context for every upload page
            context = {
                "report_id": report_id,
            }
            # Using the current URL, append page specific context
            path_name = request.path.split("/")[2]

            context["view_id"] = self.additional_context[path_name]["view_id"]
            context["section_name"] = self.additional_context[path_name]["section_name"]

            return render(request, "report_submission/delete-file-page.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        # SOT TODO: Post SOT Launch -> Remove SAC / SubmissionEvent
        report_id = kwargs["report_id"]
        path_name = request.path.split("/")[2]
        section = self.additional_context[path_name]
        redirect_uri = f"/report_submission/{section['view_id']}/{report_id}"
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            accesses = Access.objects.filter(sac=sac, user=request.user)

            audit = Audit.objects.find_audit_or_none(report_id=report_id)
            # accesses = Access.objects.filter(audit=audit, user=request.user)

            if not accesses:
                messages.error(request, "You do not have access to this audit.")
                return Util.validate_redirect_url(redirect_uri)

            try:
                excel_files = ExcelFile.objects.filter(
                    sac=sac, form_section=section["form_section"]
                )
                logger.info(f"Deleting {excel_files.count()} files.")
                excel_files.delete()

                setattr(sac, section["field_name"], None)
                sac.save()

                if audit:
                    del audit.audit[section["field_name"]]
                    audit.save(
                        event_type=section["event_type"],
                        event_user=request.user,
                    )
            except ExcelFile.DoesNotExist:
                messages.error(request, "File not found.")
                return Util.validate_redirect_url(redirect_uri)

            # SOT TODO: Switch to `audit`. Also, this should generate a
            # History event, as opposed to a SubmissionEvent
            SubmissionEvent.objects.create(
                sac_id=sac.id,
                # SOT TODO: audit MUST exist at this point, but we're not
                # connecting it up *yet* because we have never tested adding in
                # this relationship. In theory, it is safe. Or, perhaps it is
                # not needed, because we won't be keeping SubmissionEvents post-SOT.
                # audit_id=audit.id if audit else None,
                user=request.user,
                event=section["event_type"],
            )

            logger.info("The file(s) has been successfully deleted.")
            return Util.validate_redirect_url(
                f"/audit/submission-progress/{sac.report_id}"
            )

        except SingleAuditChecklist.DoesNotExist:
            logger.error(f"Audit: {report_id} not found")
            messages.error(request, "Audit not found.")
            return Util.validate_redirect_url(redirect_uri)

        except Exception as e:
            logger.error(f"Unexpected error in DeleteFileView post: {str(e)}")
            messages.error(request, "An unexpected error occurred.")
            return Util.validate_redirect_url(redirect_uri)


# TODO: Update Post SOC Launch -> Compare methods can be deleted, handle_sot_beta can be used above
def _compare_shapes(sac_shape, audit_shape):
    if sac_shape != audit_shape:
        logger.error(
            f"<SOT ERROR> SAC and Audit Shape do not match SAC: {sac_shape} Audit: {audit_shape}"
        )


def _compare_completed_metadata(sac_result, audit_result):
    if sac_result != audit_result:
        logger.error(
            f"<SOT ERROR> SAC and Audit Results do not match SAC: {sac_result} Audit: {audit_result}"
        )


def _handle_sot_beta_upload_get(request, *args, **kwargs):
    report_id = kwargs["report_id"]

    audit = Audit.objects.find_audit_or_none(report_id=report_id)
    if not audit:
        raise PermissionDenied("You do not have access to this audit.")

    path_name = request.path.split("/")[2]
    additional_context = create_upload_context(report_id)
    context = {
        "auditee_name": audit.auditee_name,
        "report_id": report_id,
        "auditee_uei": audit.auditee_uei,
        "user_provided_organization_type": audit.organization_type,
        "is_beta": True,
        "non_beta_url": f"report_submission:{path_name}",
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
