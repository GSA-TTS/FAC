import json
from pprint import pprint

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


class SacSaveFormView(APIView):
    """
    Saves a form!
    """

    missing_items = []

    def field_check_and_save(
            self, request, sac_object, request_field_name, sac_field_name
    ):
        value = request.data.get(request_field_name)
        if value is None:
            return request_field_name
        else:
            sac_object.__dict__[sac_field_name] = value

    def add_user_access(self, email, role):
        new_access = Access()
        new_access.email = email
        new_access.role = role
        new_access.save()
        return new_access

    def post(self, request):

        try:
            sac = SingleAuditChecklist()
            missing_items = []

            # 1. Go through each field of request.data
            # Page 1
            missing_items.append(
                self.field_check_and_save(
                    request,
                    sac,
                    "user_provided_organization_type",
                    "user_provided_organization_type",
                )
            )
            missing_items.append(
                self.field_check_and_save(
                    request, sac, "met_spending_threshold", "met_spending_threshold"
                )
            )
            missing_items.append(
                self.field_check_and_save(request, sac, "is_usa_based", "is_usa_based")
            )

            # Page 2
            missing_items.append(
                self.field_check_and_save(request, sac, "auditee_ueid", "auditee_uei")
            )
            missing_items.append(
                self.field_check_and_save(request, sac, "auditee_name", "auditee_name")
            )
            missing_items.append(
                self.field_check_and_save(
                    request,
                    sac,
                    "auditee_fy_start_date_start",
                    "auditee_fiscal_period_start",
                )
            )
            missing_items.append(
                self.field_check_and_save(
                    request, sac, "auditee_fy_start_date_end", "auditee_fiscal_period_end"
                )
            )

            # Page 3
            if request.data.get("auditee_certifying_official_name") is None:
                missing_items.append("auditee_certifying_official_name")
            if request.data.get("auditee_certifying_official_email") is None:
                missing_items.append("auditee_certifying_official_email")
            if request.data.get("auditor_certifying_official_name") is None:
                missing_items.append("auditor_certifying_official_name")
            if request.data.get("auditor_certifying_official_email") is None:
                missing_items.append("auditor_certifying_official_email")

            if request.data.getlist("auditee_contacts_name") is None:
                missing_items.append("auditee_contacts_name")
            if request.data.getlist("auditee_contacts_email") is None:
                missing_items.append("auditee_contacts_email")
            if request.data.getlist("auditee_contacts_name") is None:
                missing_items.append("auditee_contacts_name")
            if request.data.getlist("auditee_contacts_email") is None:
                missing_items.append("auditee_contacts_email")

            # 4. Missing fields?
            # remove all Nones first since some of the checks could add that in

            missing_items = list(filter(None, missing_items))

            if len(missing_items) > 0:
                return Response({
                    "valid": False,
                    "missing_items": missing_items
                })

            # all fields should exist at this point

            # 5. Add users
            # for each contact:
            #    make user
            #    make access
            #    if errors:
            #       rollback?
            # make SAC with accesses
            auditee_certifying_official_email_access = Access()
            auditee_certifying_official_email_access.email = (
                request.data.auditee_certifying_official_email
            )
            auditee_certifying_official_email_access.role = "auditee_cert"
            auditee_certifying_official_email_access.save()
            sac.certifying_auditee_contact = auditee_certifying_official_email_access

            auditor_certifying_official_email_access = Access()
            auditor_certifying_official_email_access.email = (
                request.data.auditor_certifying_official_email
            )
            auditor_certifying_official_email_access.role = "auditor_cert"
            auditor_certifying_official_email_access.save()
            sac.certifying_auditor_contact = auditor_certifying_official_email_access

            for email in request.data.getlist("auditee_contacts_email"):
                sac.auditee_contacts.append(self.add_user_access(email, "auditee_contact"))

            for email in request.data.getlist("auditor_contacts_email"):
                sac.auditor_contacts.append(self.add_user_access(email, "auditor_contact"))

            # 5. Apply it to SAC
            sac.save()

            # 7. Return finally
            return Response(
                {
                    "valid": True,
                    "response": sac.serializable_value(),
                }
            )

        except Exception as e:
            return Response(
                {
                    "valid": False,
                    "error": str(e),
                }
            )


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


class AccessAndSubmissionView(APIView):
    DATA_WE_NEED = AuditeeInfoView.DATA_WE_NEED + [
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
