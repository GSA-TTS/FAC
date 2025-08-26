import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404

from dissemination.models import General
from users.permissions import can_read_tribal
from audit.models.constants import RESUBMISSION_STATUS


logger = logging.getLogger(__name__)


class ReportAccessRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            general = General.objects.get(report_id=report_id)
        except General.DoesNotExist:
            raise Http404()

        self._check_resubmission_permission(request, general)

        if general.is_public:
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

    def _check_resubmission_permission(request, general):
        """
        Check permissions related to resubmissions. Raises PermissionDenied if
        not permitted.
        """
        # If the resubmission_status is None
        if not general.resubmission_status:
            pass
        # If the resubmission is a recent/current one
        elif general.resubmission_status in [
            RESUBMISSION_STATUS.MOST_RECENT,
            RESUBMISSION_STATUS.ORIGINAL,
        ]:
            pass
        # If you have privileged access, you can see old/resubmitted reports
        elif (
            general.resubmission_status == RESUBMISSION_STATUS.DEPRECATED
            and request.user
            and can_read_tribal(request.user)
        ):
            pass
        # If you are not logged in, or not privileged, and it is deprecated,
        # we need to deny.
        elif general.resubmission_status == RESUBMISSION_STATUS.DEPRECATED:
            raise PermissionDenied
        # In case we add new statuses in the future, we want to fail here
        # And, if we're wrong, it should be `pass`. However, the safe
        # thing to do is to fail here; we should explicitly encode all of
        # the conditions we 'pass' in case of resubmissions.
        else:
            raise PermissionDenied


class FederalAccessRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user:
                logger.debug(f"Denying anonymous user access to {request.path}")
                raise PermissionDenied

            if not request.user.is_authenticated:
                logger.debug(f"Denying anonymous user access to {request.path}")
                raise PermissionDenied

            if not can_read_tribal(request.user):
                logger.debug(
                    f"Denying non-priviledged user {request.user.email} access to {request.path}"
                )
                raise PermissionDenied

            return super().dispatch(request, *args, **kwargs)

        # If request.user doesn't exist, we'll see an AttributeError.
        # We still want to deny unauthenticated requests.
        except AttributeError:
            raise PermissionDenied
