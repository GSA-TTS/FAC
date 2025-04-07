import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404

from audit.models import Audit
from users.permissions import can_read_tribal


logger = logging.getLogger(__name__)


class ReportAccessRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            audit = Audit.objects.get(report_id=report_id)

            if audit.is_public:
                return super().dispatch(request, *args, **kwargs)

            if not request.user:
                logger.debug(
                    f"denying anonymous user access to non-public report {report_id}"
                )
                raise PermissionDenied

            if not request.user.is_authenticated:
                logger.debug(
                    f"denying anonymous user access to non-public report {report_id}"
                )
                raise PermissionDenied

            if not can_read_tribal(request.user):
                logger.debug(
                    f"denying user {request.user.email} access to non-public report {report_id}"
                )
                raise PermissionDenied

            return super().dispatch(request, *args, **kwargs)

        except Audit.DoesNotExist:
            raise Http404()
