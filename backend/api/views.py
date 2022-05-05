import json
import logging

from audit.models import Access, SingleAuditChecklist
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from samgov.client import SAMClient

from .serializers import (
    AccessSerializer,
    AuditeeInfoSerializer,
    EligibilitySerializer,
    SingleAuditChecklistSerializer,
    UEISerializer,
)

logger = logging.getLogger(__name__)


class SACViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SACs to be viewed.
    """

    allowed_methods = ["GET"]
    queryset = SingleAuditChecklist.objects.all()
    serializer_class = SingleAuditChecklistSerializer

    def get_view_name(self):
        return "SF-SAC"


class EligibilityFormView(APIView):
    """
    Accepts SF-SAC eligibility form responses, determines eligibility, and returns either
    messages describing ineligibility or a reference to the next step in submitted an SF-SAC.
    """

    def post(self, request):
        serializer = EligibilitySerializer(data=request.data)
        if serializer.is_valid():
            next_step = reverse("auditee-info")

            # Store step 0 data in profile, overwriting any pre-existing.
            request.user.profile.entry_form_data = request.data
            request.user.profile.save()

            return Response({"eligible": True, "next": next_step})

        return Response({"eligible": False, "errors": serializer.errors})


class UEIValidationView(APIView):
    """
    Accepts UEI to validate and returns either a message describing the validation errors, or valid.
    """

    def post(self, request):
        serializer = UEISerializer(data=request.data)

        if serializer.is_valid():
            # Local checks passed, reach out to SAM.gov for auditee Name
            uei = serializer.data.get("uei")

            try:
                auditee_name = SAMClient().get_entity_legal_name(
                    request.data.get("uei")
                )
            except ValueError as e:
                # No UEI match reported by SAM.gov
                return Response({"valid": False, "error": str(e)})
            except Exception as e:  # noqa
                # Any other exceptions raised during the request/response cycle to sam.gov means we can't retrieve auditee_name
                logger.warn(f"Unexpected SAM.gov API response: {e}")
                return Response(
                    {
                        "valid": False,
                        "error": "We encountered an unexpected error while confirming this UEI.",
                    }
                )

            # Store SAM.gov provided legal entity name in profile for later steps
            request.user.profile.entry_form_data["uei"] = uei
            request.user.profile.entry_form_data["auditee_name"] = auditee_name
            request.user.profile.save()

            return Response({"valid": True, "uei": uei, "auditee_name": auditee_name})

        return Response({"valid": False, "errors": serializer.errors})


class AuditeeInfoView(APIView):
    """
    Handle inbound requests for the `Auditee Information` step
    """

    DATA_WE_NEED = [
        "is_usa_based",
        "user_provided_organization_type",
        "met_spending_threshold",
    ]

    def post(self, request):
        serializer = AuditeeInfoSerializer(data=request.data)

        # Need Eligibility info to procede
        entry_form_data = request.user.profile.entry_form_data
        missing_fields = [
            field for field in self.DATA_WE_NEED if field not in entry_form_data
        ]
        if missing_fields:
            return Response(
                {
                    "next": reverse("eligibility"),
                    "errors": "We're missing important data, please try again.",
                }
            )

        if serializer.is_valid():
            profile_data = request.user.profile.entry_form_data

            # Check that inbound UEI and Auditee match those stored in the user's profile as responses from SAM.gov
            if (
                profile_data["uei"] != serializer.data["uei"]
                or profile_data["auditee_name"] != serializer.data["auditee_name"]
            ):
                return Response(
                    {
                        "errors": [
                            f"The provided UEI: {serializer.data['uei']} has not been validated by SAM.gov"
                        ]
                    }
                )

            next_step = reverse("access")
            # combine with expected eligibility info from session
            request.user.profile.entry_form_data = (
                request.user.profile.entry_form_data | request.data
            )
            request.user.profile.save()

            return Response({"next": next_step})

        return Response({"errors": serializer.errors})


class AccessView(APIView):
    DATA_WE_NEED = AuditeeInfoView.DATA_WE_NEED + [
        "uei",
        "auditee_fiscal_period_start",
        "auditee_fiscal_period_end",
        "auditee_name",
    ]

    def post(self, request):
        serializer = AccessSerializer(data=request.data, many=True)

        # Need Eligibility and AuditeeInfo already collected to proceed
        entry_form_data = request.user.profile.entry_form_data
        missing_fields = [
            field for field in self.DATA_WE_NEED if field not in entry_form_data
        ]
        if missing_fields:
            return Response(
                {
                    "next": reverse("eligibility"),
                    "errors": "We're missing important data, please try again.",
                }
            )

        if serializer.is_valid():
            # Create SF-SAC instance and user provided access grants
            sac = SingleAuditChecklist.objects.create(
                submitted_by=request.user, **entry_form_data
            )
            access_grants = [Access(sac=sac, **acc) for acc in serializer.data]
            Access.objects.bulk_create(access_grants)

            # Clear entry form data from profile
            request.user.profile.entry_form_data = {}
            request.user.profile.save()

            return Response({"sac_id": sac.id, "next": "TBD"})

        return Response({"errors": serializer.errors})
