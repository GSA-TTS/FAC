import logging

from django.http import Http404, JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from audit.models import Audit, Access

from audit.permissions import AuditPermission
from ..serializers import AuditSerializer

logger = logging.getLogger(__name__)

UserModel = get_user_model()


def get_role_emails_for_audit(audit_id) -> dict:
    """
    Given a audit id, returns a dictionary containing the various email addresses
    from Access objects associated with that Audit, grouped by role.

    {
        "editors": ["a@a.com", "b@b.com", "victor@frankenstein.com"]
        "certfying_auditor_contact": ["c@c.com"],
        "certfying_auditee_contact": ["e@e.com"],
    }
    """
    accesses = Access.objects.filter(audit=audit_id)

    # Turn lists into single items or None for the certifier roles:
    only_one = lambda x: x[0] if x else None
    return {
        "editors": [a.email for a in accesses if a.role == "editor"],
        "certifying_auditee_contact": only_one(
            [a.email for a in accesses if a.role == "certifying_auditee_contact"]
        ),
        "certifying_auditor_contact": only_one(
            [a.email for a in accesses if a.role == "certifying_auditor_contact"]
        ),
    }


class AuditView(APIView):
    permission_classes = [IsAuthenticated, AuditPermission]
    invalid_metadata_keys = [
        "submitted_by",
        "date_created",
        "submission_status",
        "report_id",
    ]

    invalid_general_information_keys = [
        "auditee_fiscal_period_start",
        "auditee_fiscal_period_end",
        "auditee_uei",
    ]

    def get(self, request, report_id):
        """
        Get the audit by report_id and return it in JSON format.
        Return 404 if it doesn't exist.
        """
        try:
            audit = Audit.objects.get(report_id=report_id)
        except Audit.DoesNotExist as e:
            raise Http404() from e
        self.check_object_permissions(request, audit)

        base_data = dict(AuditSerializer(audit).data.items())
        full_data = base_data | get_role_emails_for_audit(audit.id)
        return JsonResponse(full_data)


class AuditAwardsView(APIView):
    """
    Accepts and returns data for a SAC's federal awards section
    """

    permission_classes = [IsAuthenticated, AuditPermission]

    def get(self, request, report_id):
        """
        Get the SAC by report_id and return the federal award section in JSON format.
        Return 404 if it doesn't exist.
        """

        # Note this is a placeholder, so we're not returning anything yet.

        try:
            audit = Audit.objects.get(report_id=report_id)
        except Audit.DoesNotExist as e:
            raise Http404() from e

        self.check_object_permissions(request, audit)

        # To do: Get federal awards info here

        return JsonResponse({})


class AuditSubmissionsView(APIView):
    """
    Returns the list of audits the current user has submitted
    """

    def get(self, request):
        all_submissions = Audit.objects.filter(created_by=request.user)
        fields = [
            "report_id",
            "submission_status",
            "auditee_uei",
            "auditee_fiscal_period_end",
            "auditee_name",
        ]
        results = map(lambda s: {k: getattr(s, k) for k in fields}, all_submissions)
        return JsonResponse(list(results), safe=False)
