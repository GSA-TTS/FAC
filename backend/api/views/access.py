import logging

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import (
    Access,
    SingleAuditChecklist,
    SubmissionEvent,
    Audit,
)
from audit.models.constants import STATUS, AuditType
from .constants import ACCESS_SUBMISSION_DATA_REQUIRED

from audit.models.access_roles import AccessRole

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
        for field in ACCESS_SUBMISSION_DATA_REQUIRED
        if field not in all_steps_user_form_data
    ]
    if missing_fields:
        return {
            "next": reverse("api-auditee-info"),
            "errors": "We're missing required fields, please try again.",
            "missing_fields": missing_fields,
        }

    if serializer.is_valid():
        # Create SF-SAC instance and add data from previous steps saved in the
        # user profile

        sac = SingleAuditChecklist.objects.create(
            submitted_by=user,
            submission_status=STATUS.IN_PROGRESS,
            general_information=all_steps_user_form_data,
            event_user=user,
            event_type=SubmissionEvent.EventType.CREATED,
            # TODO: Update Post SOC Launch
            # migrated_to_audit should be true IF AND ONLY IF the Audit is being generated alongside the checklist.
            migrated_to_audit=True,
        )

        # TODO: Update Post SOC Launch
        # TODO: we will need to generate our own report_id when we deprecate "sac" from this workflow.
        audit = Audit.objects.create(
            report_id=sac.report_id,  # TODO Temporarily use the current id to mirror
            submission_status=STATUS.IN_PROGRESS,
            audit_type=AuditType.SINGLE_AUDIT,
            audit={
                "general_information": all_steps_user_form_data,
                "type_audit_code": "UG",
            },
            event_user=user,
            event_type=SubmissionEvent.EventType.CREATED,
        )

        # Create all contact Access objects
        # TODO: Update Post SOC Launch
        # Remove references to sac for all 5 Access creations.
        Access.objects.create(
            sac=sac,
            audit=audit,
            role="editor",
            email=str(user.email).lower(),
            user=user,
            event_user=user,
            event_type=SubmissionEvent.EventType.ACCESS_GRANTED,
        )
        Access.objects.create(
            sac=sac,
            audit=audit,
            role=AccessRole.CERTIFYING_AUDITEE_CONTACT,
            fullname=serializer.data.get("certifying_auditee_contact_fullname"),
            email=serializer.data.get("certifying_auditee_contact_email").lower(),
            event_user=user,
            event_type=SubmissionEvent.EventType.ACCESS_GRANTED,
        )
        Access.objects.create(
            sac=sac,
            audit=audit,
            role=AccessRole.CERTIFYING_AUDITOR_CONTACT,
            fullname=serializer.data.get("certifying_auditor_contact_fullname"),
            email=serializer.data.get("certifying_auditor_contact_email").lower(),
            event_user=user,
            event_type=SubmissionEvent.EventType.ACCESS_GRANTED,
        )

        # Once we get here, it should be impossible for these user values to be missing.
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
                    sac=sac,
                    audit=audit,
                    role=AccessRole.EDITOR,
                    fullname=name,
                    email=str(email).lower(),
                    event_user=user,
                    event_type=SubmissionEvent.EventType.ACCESS_GRANTED,
                )

        # Clear entry form data from profile
        user.profile.entry_form_data = {}
        user.profile.save()

        # 'next' is the next step, but we have changed how we determine what is next.
        # And, we no longer strictly require general_info to be "next." This mechanism
        # probably needs revisiting.
        return {"report_id": sac.report_id, "next": "TBD"}

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
    Returns a summary list of SingleAuditChecklists that the user has Access to
    """

    def get(self, request):
        accesses = Access.objects.select_related("sac").filter(user=request.user)

        serializer = AccessListSerializer(accesses, many=True)

        return Response(serializer.data)
