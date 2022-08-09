import json

from audit.models import Access, SingleAuditChecklist
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse

from .serializers import (
    AccessAndSubmissionSerializer,
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
    Accepts information from Step 1 (Submission criteria check) of the "Create New Audit"
    pre-SAC checklist. It saves the information to the user profile and returns either
    messages describing ineligibility or a reference to the next step to advance to.
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
    Accepts information from Step 2 (Auditee information) of the "Create New Audit"
    pre-SAC checklist. It saves the information to the user profile and returns either
    messages describing missing info or a reference to the next step to advance to.
    """

    PREVIOUS_STEP_DATA_WE_NEED = [
        "user_provided_organization_type",
        "met_spending_threshold",
        "is_usa_based",
    ]

    def post(self, request):
        serializer = AuditeeInfoSerializer(data=request.data)

        # Need Eligibility info to proceed
        entry_form_data = request.user.profile.entry_form_data
        missing_fields = [
            field
            for field in self.PREVIOUS_STEP_DATA_WE_NEED
            if field not in entry_form_data
        ]
        if missing_fields:
            return Response(
                {
                    "next": reverse("eligibility"),
                    "errors": "We're missing required fields, please try again.",
                    "missing_fields": missing_fields,
                }
            )

        if serializer.is_valid():
            next_step = reverse("accessandsubmission")

            # combine with expected eligibility info from session
            request.user.profile.entry_form_data = (
                request.user.profile.entry_form_data | request.data
            )
            request.user.profile.save()

            return Response({"next": next_step})

        return Response({"errors": serializer.errors})


class AccessAndSubmissionView(APIView):
    """
    Accepts information from Step 3 (Audit submission access) of the "Create New Audit"
    pre-SAC checklist. This is the last step. It saves the information to the user profile.
    If it has all the information needed, it attempts to create user access permissions and
    then returns success or error messages.
    """

    PREVIOUS_STEP_DATA_WE_NEED = AuditeeInfoView.PREVIOUS_STEP_DATA_WE_NEED + [
        "auditee_fiscal_period_start",
        "auditee_fiscal_period_end",
    ]

    def post(self, request):
        serializer = AccessAndSubmissionSerializer(data=request.data)

        # Need Eligibility and AuditeeInfo already collected to proceed
        all_steps_user_form_data = request.user.profile.entry_form_data
        missing_fields = [
            field
            for field in self.PREVIOUS_STEP_DATA_WE_NEED
            if field not in all_steps_user_form_data
        ]
        if missing_fields:
            return Response(
                {
                    "next": reverse("eligibility"),
                    "errors": "We're missing required fields, please try again.",
                    "missing_fields": missing_fields,
                }
            )

        if serializer.is_valid():
            # Create SF-SAC instance and add data from previous steps saved in the
            # user profile
            sac = SingleAuditChecklist.objects.create(
                submitted_by=request.user, **all_steps_user_form_data
            )

            # Create all contact Access objects
            Access.objects.create(
                sac=sac, role="creator", email=request.user.email, user=request.user
            )
            Access.objects.create(
                sac=sac,
                role="auditee_cert",
                email=serializer.data.get("certifying_auditee_contact"),
            )
            Access.objects.create(
                sac=sac,
                role="auditor_cert",
                email=serializer.data.get("certifying_auditor_contact"),
            )
            for contact in serializer.data.get("auditee_contacts"):
                Access.objects.create(sac=sac, role="auditee_contact", email=contact)
            for contact in serializer.data.get("auditor_contacts"):
                Access.objects.create(sac=sac, role="auditor_contact", email=contact)

            sac.save()

            # Clear entry form data from profile
            request.user.profile.entry_form_data = {}
            request.user.profile.save()

            return Response({"sac_id": sac.id, "next": "TBD"})

        return Response({"errors": serializer.errors})


class SubmissionsView(APIView):
    """
    Returns the list of SingleAuditChecklists the current user has submitted
    """

    def get(self, request):
        current_user = request.user

        all_submissions = SingleAuditChecklist.objects.filter(
            submitted_by=current_user
        ).values(
            "report_id",
            "submission_status",
            "auditee_uei",
            "auditee_fiscal_period_end",
            "auditee_name",
        )

        return JsonResponse(list(all_submissions), safe=False)
