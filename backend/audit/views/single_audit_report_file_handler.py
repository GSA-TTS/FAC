import logging

from django.views import generic
from django.shortcuts import redirect
from django.core.exceptions import BadRequest
from django.utils.datastructures import MultiValueDictKeyError

from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    SingleAuditChecklist,
    SingleAuditReportFile,
    Audit,
)
from audit.models.constants import EventType

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class SingleAuditReportFileHandlerView(
    SingleAuditChecklistAccessRequiredMixin, generic.View
):
    def post(self, request, *args, **kwargs):
        try:
            report_id = kwargs["report_id"]

            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            audit = Audit.objects.find_audit_or_none(report_id=report_id)
            file = request.FILES["FILES"]

            sar_file = SingleAuditReportFile(
                **{
                    "file": file,
                    "filename": "temp",
                    "sac_id": sac.id,
                    "audit_id": audit.id if audit else None,
                }
            )

            sar_file.full_clean()
            sar_file.save(
                event_user=request.user,
                event_type=EventType.AUDIT_REPORT_PDF_UPDATED,
            )

            return redirect("/")

        except MultiValueDictKeyError:
            logger.warning("No file found in request")
            raise BadRequest()
