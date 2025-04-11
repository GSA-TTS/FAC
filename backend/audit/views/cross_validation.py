import logging

from django.views import generic
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import Audit

from audit.decorators import verify_status
from audit.models.constants import STATUS

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class CrossValidationView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    @verify_status(STATUS.IN_PROGRESS)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = Audit.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }
            return render(
                request, "audit/cross-validation/cross-validation.html", context
            )
        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.IN_PROGRESS)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
            audit_errors = audit.validate()

            context = {"report_id": report_id, "errors": audit_errors}

            return render(
                request, "audit/cross-validation/cross-validation-results.html", context
            )

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
