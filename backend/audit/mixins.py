from typing import Any

from audit.exceptions import SessionExpiredException
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from .models import Access, Audit
from .models.access_roles import AccessRole

User = get_user_model()


PERMISSION_DENIED_MESSAGE = "You do not have access to this audit."


class CertificationPermissionDenied(PermissionDenied):
    def __init__(self, message, eligible_users):
        super().__init__(message)

        self.eligible_users = eligible_users


def check_authenticated(request):
    if not hasattr(request, "user") or not request.user:
        raise PermissionDenied(PERMISSION_DENIED_MESSAGE)
    if not request.user.is_authenticated:
        raise SessionExpiredException()


def has_access_to_audit(audit, user):
    """Does a user have permission to access a submission?"""
    return bool(Access.objects.filter(audit=audit, user=user))


def has_role_on_audit(audit, user, role):
    """Does a user have a specific role on a submission?"""
    return (
        bool(Access.objects.filter(audit=audit, user=user, role=role)) if role else True
    )


ACCESS_ROLE_ERROR_MESSAGES = {
    AccessRole.CERTIFYING_AUDITEE_CONTACT: "Invalid role. User is not the Auditee Certifying Official",
    AccessRole.CERTIFYING_AUDITOR_CONTACT: "Invalid role. User is not the Auditor Certifying Official",
}


def _validate_access(request, report_id, role=None):
    try:
        audit = Audit.objects.get(report_id=report_id)
        check_authenticated(request)

        audit = Audit.objects.get(report_id=report_id)

        if not has_access_to_audit(audit, request.user) and not settings.DISABLE_AUTH:
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

        if not has_role_on_audit(audit, request.user, role):
            eligible_accesses = Access.objects.select_related("user").filter(
                audit=audit, role=role
            )
            eligible_users = [acc.user for acc in eligible_accesses]

            raise CertificationPermissionDenied(
                ACCESS_ROLE_ERROR_MESSAGES[role],
                eligible_users=eligible_users,
            )
    except Audit.DoesNotExist:
        raise PermissionDenied(PERMISSION_DENIED_MESSAGE)


class SingleAuditChecklistAccessRequiredMixin(LoginRequiredMixin):
    """
    View mixin to require that a user is logged in and has access to the submission.
    """

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        _validate_access(request=request, report_id=kwargs.get("report_id"))
        return super().dispatch(request, *args, **kwargs)


class CertifyingAuditeeRequiredMixin(LoginRequiredMixin):
    """
    View mixin to require that a user is logged in, has access to the submission, and has
    the ``certifying_auditee_contact`` role.
    """

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        _validate_access(
            request=request,
            report_id=kwargs.get("report_id"),
            role=AccessRole.CERTIFYING_AUDITEE_CONTACT,
        )
        return super().dispatch(request, *args, **kwargs)


class CertifyingAuditorRequiredMixin(LoginRequiredMixin):
    """
    View mixin to require that a user is logged in, has access to the submission, and has
    the ``certifying_auditor_contact`` role.
    """

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        _validate_access(
            request=request,
            report_id=kwargs.get("report_id"),
            role=AccessRole.CERTIFYING_AUDITOR_CONTACT,
        )
        return super().dispatch(request, *args, **kwargs)
