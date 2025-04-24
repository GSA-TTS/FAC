import logging

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import (
    Access,
    Audit,
)
from audit.models.constants import STATUS, AuditType, EventType
from .constants import ACCESS_SUBMISSION_PREVIOUS_STEP_DATA_WE_NEED

from ..serializers import AccessListSerializer, AccessAndSubmissionSerializer

logger = logging.getLogger(__name__)

UserModel = get_user_model()


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
        audit = Audit.objects.create(
            submission_status=STATUS.IN_PROGRESS,
            audit_type=AuditType.SINGLE_AUDIT,
            audit={"general_information": all_steps_user_form_data},
            event_user=user,
            event_type=EventType.CREATED,
        )

        # Create all contact Access objects
        # Remove references to sac for all 5 Access creations.
        Access.objects.create(
            audit=audit,
            role="editor",
            email=str(user.email).lower(),
            user=user,
            event_user=user,
            event_type=EventType.ACCESS_GRANTED,
        )
        Access.objects.create(
            audit=audit,
            role="certifying_auditee_contact",
            fullname=serializer.data.get("certifying_auditee_contact_fullname"),
            email=serializer.data.get("certifying_auditee_contact_email").lower(),
            event_user=user,
            event_type=EventType.ACCESS_GRANTED,
        )
        Access.objects.create(
            audit=audit,
            role="certifying_auditor_contact",
            fullname=serializer.data.get("certifying_auditor_contact_fullname"),
            email=serializer.data.get("certifying_auditor_contact_email").lower(),
            event_user=user,
            event_type=EventType.ACCESS_GRANTED,
        )

        # The contacts form should prevent users from submitting an incomplete contacts section
        auditee_contacts_info = zip(
            serializer.data.get("auditee_contacts_email"),
            serializer.data.get("auditee_contacts_fullname"),
        )

        auditor_contacts_info = zip(
            serializer.data.get("auditor_contacts_email"),
            serializer.data.get("auditor_contacts_fullname"),
        )

        all_contacts = list(auditee_contacts_info) + list(auditor_contacts_info)
        for email, name in all_contacts:
            if email:
                Access.objects.create(
                    audit=audit,
                    role="editor",
                    fullname=name,
                    email=str(email).lower(),
                    event_user=user,
                    event_type=EventType.ACCESS_GRANTED,
                )

        # Clear entry form data from profile
        user.profile.entry_form_data = {}
        user.profile.save()

        return {"report_id": audit.report_id, "next": "TBD"}

    return {
        "errors": serializer.errors,
        "certifying_auditee_contact_fullname": data.get(
            "certifying_auditee_contact_fullname"
        ),
        "certifying_auditee_contact_email": data.get(
            "certifying_auditee_contact_email"
        ),
        "certifying_auditee_contact_re_email": data.get(
            "certifying_auditee_contact_re_email"
        ),
        "certifying_auditor_contact_fullname": data.get(
            "certifying_auditor_contact_fullname"
        ),
        "certifying_auditor_contact_email": data.get(
            "certifying_auditor_contact_email"
        ),
        "certifying_auditor_contact_re_email": data.get(
            "certifying_auditor_contact_re_email"
        ),
    }


class AccessAndSubmissionView(APIView):
    """
    Accepts information from Step 3 (Audit submission access) of the "Create New Audit"
    pre-SAC checklist. This is the last step. It saves the information to the user profile.
    If it has all the information needed, it attempts to create user access permissions and
    then returns success or error messages.
    """

    def post(self, request):
        return Response(access_and_submission_check(request.user, request.data))


class AccessListView(APIView):
    """
    Returns a summary list of Audits that the user has Access to
    """

    def get(self, request):
        accesses = Access.objects.select_related("audit").filter(user=request.user)

        serializer = AccessListSerializer(accesses, many=True)

        return Response(serializer.data)
