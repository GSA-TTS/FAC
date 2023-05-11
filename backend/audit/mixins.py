from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.core.exceptions import PermissionDenied

from .models import Access, SingleAuditChecklist


def has_access(report_id, user, *args, **kwargs):
    try:
        sac = SingleAuditChecklist.objects.get(report_id=report_id)

        accesses = Access.objects.filter(sac=sac, user=user, **kwargs)
        if not accesses:
            return False

        return True

    except SingleAuditChecklist.DoesNotExist:
        return False


class SingleAuditChecklistAccessRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        report_id = kwargs["report_id"]

        if has_access(report_id, request.user):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You do not have access to this audit.")


class CertifyingAuditeeRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        report_id = kwargs["report_id"]

        if has_access(report_id, request.user, role="certifying_auditee_contact"):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You do not have access to this audit.")


class CertifyingAuditorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        report_id = kwargs["report_id"]

        if has_access(report_id, request.user, role="certifying_auditor_contact"):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You do not have access to this audit.")
