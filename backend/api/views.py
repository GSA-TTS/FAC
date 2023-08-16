import json
from typing import List

from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.views import View, generic
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.settings import AUDIT_SCHEMA_DIR, BASE_DIR
from audit.models import Access, SingleAuditChecklist
from audit.permissions import SingleAuditChecklistPermission
from .serializers import (
    AccessAndSubmissionSerializer,
    AccessListSerializer,
    AuditeeInfoSerializer,
    EligibilitySerializer,
    SingleAuditChecklistSerializer,
    UEISerializer,
)

UserModel = get_user_model()

AUDITEE_INFO_PREVIOUS_STEP_DATA_WE_NEED = [
    "user_provided_organization_type",
    "met_spending_threshold",
    "is_usa_based",
]

AUDITEE_INFO_STEP_TWO_FIELDS = [
    "auditee_fiscal_period_start",
    "auditee_fiscal_period_end",
]

ACCESS_SUBMISSION_PREVIOUS_STEP_DATA_WE_NEED = (
    AUDITEE_INFO_PREVIOUS_STEP_DATA_WE_NEED + AUDITEE_INFO_STEP_TWO_FIELDS
)


def eligibility_check(user, data):
    serializer = EligibilitySerializer(data=data)  # data = request.data
    # self.eligibility_check(request)
    if serializer.is_valid():
        next_step = reverse("api-auditee-info")

        # Store step 0 data in profile, overwriting any pre-existing.
        user.profile.entry_form_data = serializer.data
        user.profile.save()
        return {"eligible": True, "next": next_step}

    return {"eligible": False, "errors": serializer.errors}


def auditee_info_check(user, data):
    serializer = AuditeeInfoSerializer(data=data)

    # Need Eligibility info to proceed
    entry_form_data = user.profile.entry_form_data

    missing_fields = [
        field
        for field in AUDITEE_INFO_PREVIOUS_STEP_DATA_WE_NEED
        if field not in entry_form_data
    ]
    if missing_fields:
        return {
            "next": reverse("api-eligibility"),
            "errors": "We're missing required fields, please try again.",
            "missing_fields": missing_fields,
        }

    if serializer.is_valid():
        next_step = reverse("api-accessandsubmission")

        # combine with expected eligibility info from session
        user.profile.entry_form_data = user.profile.entry_form_data | data
        user.profile.save()

        return {"next": next_step}

    return {"errors": serializer.errors}


def access_and_submission_check(user, data):
    serializer = AccessAndSubmissionSerializer(data=data)

    # Need Eligibility and AuditeeInfo already collected to proceed.
    # We probably need to exclude more than just csrfmiddlewaretoken from
    # stray properties that might end up present in the submitted data:
    all_steps_user_form_data = {
        k: user.profile.entry_form_data[k]
        for k in user.profile.entry_form_data
        if k != "csrfmiddlewaretoken"
    }
    missing_fields = [
        field
        for field in ACCESS_SUBMISSION_PREVIOUS_STEP_DATA_WE_NEED
        if field not in all_steps_user_form_data
    ]
    if missing_fields:
        return {
            "next": reverse("api-eligibility"),
            "errors": "We're missing required fields, please try again.",
            "missing_fields": missing_fields,
        }

    if serializer.is_valid():
        # Create SF-SAC instance and add data from previous steps saved in the
        # user profile

        sac = SingleAuditChecklist.objects.create(
            submitted_by=user,
            submission_status="in_progress",
            general_information=all_steps_user_form_data,
        )

        print(f"🔶 {user.profile}")
        # Create all contact Access objects
        Access.objects.create(
            sac=sac,
            role="editor",
            email=user.email,
            user=user,
        )
        Access.objects.create(
            sac=sac,
            role="certifying_auditee_contact",
            fullname=serializer.data.get("certifying_auditee_contact_fullname"),
            email=serializer.data.get("certifying_auditee_contact_email"),
        )
        Access.objects.create(
            sac=sac,
            role="certifying_auditor_contact",
            fullname=serializer.data.get("certifying_auditor_contact_fullname"),
            email=serializer.data.get("certifying_auditor_contact_email"),
        )

        # This fails if you leave out a name. "index" is undefined.
        for index, email in enumerate(serializer.data.get("auditee_contacts_email")):
            print(f"📇 {index}")
            print(f"📇 {email}")
            Access.objects.create(
                sac=sac,
                role="editor",
                fullname=serializer.data.get("auditee_contacts_fullname")[index],
                email=email,
            )
        for index, email in enumerate(serializer.data.get("auditor_contacts_email")):
            Access.objects.create(
                sac=sac,
                role="editor",
                fullname=serializer.data.get("auditor_contacts_fullname"),
                email=email,
            )

        sac.save()

        # Clear entry form data from profile
        user.profile.entry_form_data = {}
        user.profile.save()

        return {"report_id": sac.report_id, "next": "TBD"}

    return {"errors": serializer.errors}


class Sprite(generic.View):
    """
    Due to problematic interactions between the SVG use element and
    cross-domain rules and serving assets from S3, we need to serve this
    particular file from Django.
    """

    def get(self, _request):
        """Grab the file from static and return its contents as an image."""
        fpath = BASE_DIR / "static" / "img" / "sprite.svg"
        return HttpResponse(
            content=fpath.read_text(encoding="utf-8"), content_type="image/svg+xml"
        )


class IndexView(View):
    def get(self, request, *args, **kwargs):
        fpath = BASE_DIR / "static" / "index.html"
        return HttpResponse(content=fpath.read_text(encoding="utf-8"))


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
        return Response(eligibility_check(request.user, request.data))


class UEIValidationFormView(APIView):
    """
    Accepts UEI to validate and returns either a message describing the validation errors, or valid.
    """

    def post(self, request):
        data = request.data
        data["auditee_uei"] = data["auditee_uei"].upper()
        serializer = UEISerializer(data=data)

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

    def post(self, request):
        return Response(auditee_info_check(request.user, request.data))


class AccessAndSubmissionView(APIView):
    """
    Accepts information from Step 3 (Audit submission access) of the "Create New Audit"
    pre-SAC checklist. This is the last step. It saves the information to the user profile.
    If it has all the information needed, it attempts to create user access permissions and
    then returns success or error messages.
    """

    def post(self, request):
        return Response(access_and_submission_check(request.user, request.data))


def get_role_emails_for_sac(sac_id) -> dict:
    """
    Given a SAC id, returns a dictionary containing the various email addresses
    from Access objects associated with that SAC, grouped by role.

    {
        "editors": ["a@a.com", "b@b.com", "victor@frankenstein.com"]
        "certfying_auditor_contact_email": ["c@c.com"],
        "certfying_auditee_contact_email": ["e@e.com"],
    }
    """
    accesses = Access.objects.filter(sac=sac_id)

    # Turn lists into single items or None for the certifier roles:
    only_one = lambda x: x[0] if x else None
    return {
        "editors": [{a.email, a.fullname} for a in accesses if a.role == "editor"],
        "certifying_auditee_contact_email": only_one(
            [a.email for a in accesses if a.role == "certifying_auditee_contact_email"]
        ),
        "certifying_auditor_contact_email": only_one(
            [a.email for a in accesses if a.role == "certifying_auditor_contact_email"]
        ),
    }


class SingleAuditChecklistView(APIView):
    """
    Accepts and returns data for a SingleAuditChecklist
    """

    permission_classes = [IsAuthenticated, SingleAuditChecklistPermission]
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

        submitted_invalid_keys = [
            k for k in self.invalid_metadata_keys if k in request.data
        ] + [
            k
            for k in self.invalid_general_information_keys
            if k in request.data.get("general_information", {})
        ]

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


class SacFederalAwardsView(APIView):
    """
    Accepts and returns data for a SAC's federal awards section
    """

    permission_classes = [IsAuthenticated, SingleAuditChecklistPermission]

    def get(self, request, report_id):
        """
        Get the SAC by report_id and return the federal award section in JSON format.
        Return 404 if it doesn't exist.
        """

        # Note this is a placeholder, so we're not returning anything yet.

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
        except SingleAuditChecklist.DoesNotExist as e:
            raise Http404() from e

        self.check_object_permissions(request, sac)

        # To do: Get federal awards info here

        return JsonResponse({})


class SubmissionsView(APIView):
    """
    Returns the list of SingleAuditChecklists the current user has submitted
    """

    def get(self, request):
        current_user = request.user

        all_submissions = SingleAuditChecklist.objects.filter(submitted_by=current_user)

        fields = [
            "report_id",
            "submission_status",
            "auditee_uei",
            "auditee_fiscal_period_end",
            "auditee_name",
        ]

        results = map(lambda s: {k: getattr(s, k) for k in fields}, all_submissions)

        return JsonResponse(list(results), safe=False)


class AccessListView(APIView):
    """
    Returns a summary list of SingleAuditChecklists that the user has Access to
    """

    def get(self, request):
        accesses = Access.objects.select_related("sac").filter(user=request.user)

        serializer = AccessListSerializer(accesses, many=True)

        return Response(serializer.data)


class SchemaView(APIView):
    """
    Returns the JSON schema for the specified fiscal year
    """

    # this is a public endpoint - no authentication or permission required
    authentication_classes: List[BaseAuthentication] = []
    permission_classes: List[BasePermission] = []

    def get(self, _, fiscal_year, schema_type):
        """GET JSON schema for the specified fiscal year"""
        fpath = AUDIT_SCHEMA_DIR / f"{fiscal_year}-{schema_type}.json"

        if not fpath.exists():
            raise Http404()

        return JsonResponse(json.loads(fpath.read_text(encoding="utf-8")))
