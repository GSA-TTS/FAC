from typing import Any
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.core.exceptions import PermissionDenied

from .models import Access, SingleAuditChecklist

User = get_user_model()


class CertificationPermissionDenied(PermissionDenied):
    def __init__(self, message, eligible_users):
        super().__init__(message)

        self.eligible_users = eligible_users


def has_access(sac, user):
    accesses = Access.objects.filter(sac=sac, user=user)
    if not accesses:
        return False

    return True


def has_role(sac, user, role):
    accesses = Access.objects.filter(sac=sac, user=user, role=role)
    if not accesses:
        return False

    return True


class SingleAuditChecklistAccessRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            report_id = kwargs["report_id"]
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            if not has_access(sac, request.user):
                raise PermissionDenied("You do not have access to this audit.")
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

        return super().dispatch(request, *args, **kwargs)


class CertifyingAuditeeRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        role = "certifying_auditee_contact"
        try:
            report_id = kwargs["report_id"]
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            if not has_access(sac, request.user):
                raise PermissionDenied("You do not have access to this audit")

            if not has_role(sac, request.user, role):
                eligible_accesses = Access.objects.select_related("user").filter(
                    sac=sac, role=role
                )
                eligible_users = [acc.user for acc in eligible_accesses]

                raise CertificationPermissionDenied(
                    "bad role", eligible_users=eligible_users
                )
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

        return super().dispatch(request, *args, **kwargs)


class CertifyingAuditorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        role = "certifying_auditor_contact"
        try:
            report_id = kwargs["report_id"]
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            if not has_access(sac, request.user):
                raise PermissionDenied("You do not have access to this audit")

            if not has_role(sac, request.user, role):
                eligible_accesses = Access.objects.select_related("user").filter(
                    sac=sac, role=role
                )
                eligible_users = [acc.user for acc in eligible_accesses]
                raise CertificationPermissionDenied(
                    "bad role", eligible_users=eligible_users
                )
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

        return super().dispatch(request, *args, **kwargs)
