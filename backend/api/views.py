import json

from audit.models import Access, SingleAuditChecklist
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AccessSerializer,
    AuditeeInfoSerializer,
    EligibilitySerializer,
    SingleAuditChecklistSerializer,
    UEISerializer,
)


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


class UEIValidationFormView(APIView):
    """
    Accepts UEI to validate and returns either a message describing the validation errors, or valid.
    """

    def post(self, request):
        serializer = UEISerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {
                    "valid": True,
                    "response": json.loads(serializer.data.get("auditee_uei")),
                }
            )
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
        "auditee_fiscal_period_start",
        "auditee_fiscal_period_end",
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
