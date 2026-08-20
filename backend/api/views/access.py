import logging

from django.db import transaction
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
from audit.models.constants import STATUS, AuditType, RESUBMISSION_ACTION
from .constants import ACCESS_SUBMISSION_DATA_REQUIRED

from audit.models.access_roles import AccessRole

from ..serializers import AccessListSerializer, AccessAndSubmissionSerializer
from audit.views.upload_report_view import copy_previous_report_data

logger = logging.getLogger(__name__)

UserModel = get_user_model()


def access_and_submission_check(user, data):
    """
    Validate the access passed in by the user. Then, create a SAC and its associated access objects.
    When successful, returns the report_id of the newly created SAC. Otherwise, returns formatted errors.

    1. Check that all other steps have been completed.
    2. Validate the accesses given by the user.
    3. Create a new SAC row. In the case of resubmission, do so via `initiate_resubmission` on the previous SAC.
    4. Create the required access objects for the SAC.
    """
    serializer = AccessAndSubmissionSerializer(data=data)

    # Need Eligibility and AuditeeInfo already collected to proceed.
    # We may want to exclude more than just these fields from the
    # stray properties that might end up present in the submitted data:
    omitted_fields = [
        "csrfmiddlewaretoken",
        "is_resubmission",  # Bool used to ensure users go through all forms
        "resubmission_meta",  # Stored in its own column
    ]
    all_steps_user_form_data = {
        k: user.profile.entry_form_data[k]
        for k in user.profile.entry_form_data
        if k not in omitted_fields
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

    resubmission_meta = user.profile.entry_form_data.get(
        "resubmission_meta", {}
    )  # Should always exist with our current flow.
    previous_report_id = resubmission_meta.get(
        "previous_report_id"
    )  # Will only exist in resubmissions

    if not serializer.is_valid():
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

    # We have this section in an atomic block. If anything goes very wrong, all DB writes will be undone.
    # This is because several writes need to happen on several tables, and leaving it half baked would be very confusing.
    # In order:
    # 1. The SAC is created.
    # 2. The Audit is created.
    # 3. If the SAC was a resubmission, it may copy data into a new SAR.
    # 4. All access objects are created for the SAC and Audit.
    try:
        with transaction.atomic():
            # 1. If the user profile indicates this is a resubmission, create a new SAC row via
            # initiate_resubmission on the old SAC. Otherwise, create a new SAC from scratch.
            if previous_report_id:
                previous_sac = SingleAuditChecklist.objects.get(
                    report_id=previous_report_id
                )
                sac = previous_sac.initiate_resubmission(user=user)

                sac.resubmission_meta = {
                    **(sac.resubmission_meta or {}),
                    **resubmission_meta,
                }
                sac.save()
            else:
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

            # 2. Create the associated Audit
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

            # 3. For SFSAC_ONLY resubmissions, automatically copy the PDF from the previous submission.
            if (
                previous_report_id
                and resubmission_meta.get("resubmission_action")
                == RESUBMISSION_ACTION.SFSAC_ONLY
            ):
                try:
                    copy_previous_report_data(
                        previous_report_id=previous_report_id,
                        current_sac=sac,
                        current_audit=audit,
                        user=user,
                    )
                except Exception as err:
                    logger.error(
                        "Unexpected error copying SingleAuditReportFile on initiate_resubmission: %s",
                        err,
                    )
                    raise

            # 4. Create all contact Access objects
            _create_access_objects(sac, audit, user, serializer)

            # Clean up user profile data, so it doesn't affect future submissions.
            user.profile.entry_form_data = {}
            user.profile.save()

    # Any and all errors will logged, and the DB writes will be un-done. We return to avoid strange 500 errors.
    except Exception as err:
        logger.error("Failed to create audit submission: %s", err)
        return {
            "errors": "An error occurred while creating your submission. Please try again. If the issue persists, please contact the helpdesk for assistance.",
        }

    # 'next' is the next step, but we have changed how we determine what is next.
    # And, we no longer strictly require general_info to be "next." This mechanism
    # probably needs revisiting.
    return {"report_id": sac.report_id, "next": "TBD"}


def _create_access_objects(sac, audit, user, serializer):
    """
    Create all Access objects for the new SAC and associated Audit.

    Broken out from `access_and_submission_check` to help readability.
    """
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
    # The contacts form should prevent users from submitting an incomplete contacts section.
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
