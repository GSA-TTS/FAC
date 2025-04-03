from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import AUDITEE_INFO_PREVIOUS_STEP_DATA_WE_NEED
from ..serializers import AuditeeInfoSerializer


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


class AuditeeInfoView(APIView):
    """
    Accepts information from Step 2 (Auditee information) of the "Create New Audit"
    pre-SAC checklist. It saves the information to the user profile and returns either
    messages describing missing info or a reference to the next step to advance to.
    """

    def post(self, request):
        return Response(auditee_info_check(request.user, request.data))
