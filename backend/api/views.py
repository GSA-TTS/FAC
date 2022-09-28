import json
from typing import List

from audit.models import Access, SingleAuditChecklist
from audit.permissions import SingleAuditChecklistPermission
from django.http import Http404
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from .serializers import (
    AccessAndSubmissionSerializer,
    AccessListSerializer,
    AuditeeInfoSerializer,
    EligibilitySerializer,
    SingleAuditChecklistSerializer,
    UEISerializer,
)


class SACViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SACs to be viewed.
    """

    # this is a public endpoint - no authentication or permission required
    authentication_classes: List[BaseAuthentication] = []
    permission_classes: List[BasePermission] = []

    allowed_methods = ["GET"]

    # lookup SACs with report_id rather than the default pk
    lookup_field = "report_id"

    queryset = SingleAuditChecklist.objects.filter(submission_status="submitted")
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
                role="certifying_auditee_contact",
                email=serializer.data.get("certifying_auditee_contact"),
            )
            Access.objects.create(
                sac=sac,
                role="certifying_auditor_contact",
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

            return Response({"report_id": sac.report_id, "next": "TBD"})

        return Response({"errors": serializer.errors})


def get_role_emails_for_sac(sac_id) -> dict:
    """
    Given a SAC id, returns a dictionary containing the various email addresses
    from Access objects associated with that SAC, grouped by role.

    {
        "auditee_contacts": ["a@a.com"],
        "auditee_contacts": ["b@b.com"],
        "certfying_auditor_contact": ["c@c.com"],
        "certfying_auditee_contact": ["e@e.com"],
        "creator": ["victor@frankenstein.com"],
    }
    """
    accesses = Access.objects.filter(sac=sac_id)

    # This is inelegant, but we have to change the name of the key for
    # two of them, and turn lists into single items or None for the
    # other two:
    only_one = lambda x: x[0] if x else None
    return {
        "auditee_contacts": [a.email for a in accesses if a.role == "auditee_contact"],
        "auditor_contacts": [a.email for a in accesses if a.role == "auditor_contact"],
        "certifying_auditee_contact": only_one(
            [a.email for a in accesses if a.role == "certifying_auditee_contact"]
        ),
        "certifying_auditor_contact": only_one(
            [a.email for a in accesses if a.role == "certifying_auditor_contact"]
        ),
        "creator": only_one([a.email for a in accesses if a.role == "creator"]),
    }


class SingleAuditChecklistView(APIView):
    """
    Accepts and returns data for a SingleAuditChecklist
    """

    permission_classes = [SingleAuditChecklistPermission]
    invalid_keys = [
        "submitted_by",
        "date_created",
        "submission_status",
        "report_id",
        "auditee_fiscal_period_start",
        "auditee_fiscal_period_end",
        "auditee_uei",
        "auditee_name",
        "auditee_address_line_1",
        "auditee_city",
        "auditee_state",
        "auditee_zip",
    ]

    def get(self, request, report_id):
        """
        Get the SAC by report_id and return it in JSON format.
        Return 404 if it doesn't exist.
        """
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
        except SingleAuditChecklist.DoesNotExist as e:
            raise Http404() from e
        self.check_object_permissions(request, sac)

        base_data = dict(SingleAuditChecklistSerializer(sac).data.items())
        full_data = base_data | get_role_emails_for_sac(sac.id)

        return JsonResponse(full_data)

    def put(self, request, report_id):
        """
        Retrieve the SAC by report_id.
        Return 404 if it doesn't exist.
        If it does, examine the submission for fields that cannot be updated
        via this endpoint and return errors (and status 400) if they are
        present.
        Otherwise, update the database entry with the submitted values and
        return the updated SAC in JSON format.
        """
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
        except SingleAuditChecklist.DoesNotExist as e:
            raise Http404() from e
        self.check_object_permissions(request, sac)

        submitted_invalid_keys = [k for k in self.invalid_keys if k in request.data]
        if submitted_invalid_keys:
            base_msg = "The following fields cannot be modified via this endpoint: "
            errors_str = ", ".join(sorted(submitted_invalid_keys))
            error_msg = f"{base_msg}{errors_str}."
            return JsonResponse({"errors": error_msg}, status=400)

        for attr, value in request.data.items():
            setattr(sac, attr, value)
        try:
            sac.full_clean()
            sac.save()
        except ValidationError as err:
            return JsonResponse({"errors": err.message_dict}, status=400)

        base_data = dict(SingleAuditChecklistSerializer(sac).data.items())
        full_data = base_data | get_role_emails_for_sac(sac.id)
        return JsonResponse(full_data)


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


class AccessListView(APIView):
    """
    Returns a summary list of SingleAuditChecklists that the user has Access to
    """

    def get(self, request):
        accesses = Access.objects.select_related("sac").filter(user=request.user)

        serializer = AccessListSerializer(accesses, many=True)

        return Response(serializer.data)
