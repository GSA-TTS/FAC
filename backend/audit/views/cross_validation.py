import logging

from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views import generic

from audit.decorators import verify_status
from audit.mixins import SingleAuditChecklistAccessRequiredMixin
from audit.models import Audit, SingleAuditChecklist
from audit.models.constants import STATUS

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class CrossValidationView(
    SingleAuditChecklistAccessRequiredMixin,
    generic.View,
):
    @verify_status(STATUS.IN_PROGRESS)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            return render(
                request,
                "audit/cross-validation/cross-validation.html",
                context,
            )

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.IN_PROGRESS)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            errors, warnings = sac.validate_full()

            audit = Audit.objects.find_audit_or_none(report_id=report_id)
            if audit:
                audit_errors, _ = audit.validate()
                _compare_errors(errors, audit_errors)

            context = {
                "report_id": report_id,
                "errors": errors,
                "warnings": warnings,
            }

            return render(
                request,
                "audit/cross-validation/cross-validation-results.html",
                context,
            )

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


# TODO: Post SOT Launch: Deletes
def _compare_errors(sac_errors, audit_errors):
    sac = sac_errors.copy() if sac_errors else {"data": {}}
    audit = audit_errors.copy() if audit_errors else {"data": {}}

    sac_metadata = sac.get("data", {}).get("sf_sac_meta", {})
    audit_metadata = audit.get("data", {}).get("sf_sac_meta", {})

    remove_fields = ("date_created", "transition_name", "transition_date")

    for field in remove_fields:
        if field in sac_metadata:
            del sac_metadata[field]

        if field in audit_metadata:
            del audit_metadata[field]

    sac["data"]["sf_sac_meta"] = sac_metadata
    audit["data"]["sf_sac_meta"] = audit_metadata

    if (sac and not audit) or (audit and not sac) or sac != audit:
        logger.error(
            f"<SOT ERROR> Cross Validation does not match: " f"SAC {sac}, Audit {audit}"
        )
