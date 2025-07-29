from django.urls import reverse

from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import AUDITEE_INFO_DATA
from ..serializers import EligibilitySerializer


def eligibility_check(user, data):
    serializer = EligibilitySerializer(data=data)

    # Need Eligibility info to proceed
    entry_form_data = user.profile.entry_form_data

    missing_fields = [
        field
        for field in AUDITEE_INFO_DATA
        if field not in entry_form_data
    ]
    if missing_fields:
        return {
            "next": reverse("api-auditee-info"),
            "errors": "We're missing required fields, please try again.",
            "missing_fields": missing_fields,
        }
    
    if serializer.is_valid():
        next_step = reverse("api-accessandsubmission")

        # Store step 2 data in profile, combined with the existing.
        user.profile.entry_form_data = user.profile.entry_form_data | data
        user.profile.save()
        return {"eligible": True, "next": next_step}

    return {"eligible": False, "errors": serializer.errors}


class EligibilityFormView(APIView):
    """
    Accepts information from Step 1 (Submission criteria check) of the "Create New Audit"
    pre-SAC checklist. It saves the information to the user profile and returns either
    messages describing ineligibility or a reference to the next step to advance to.
    """

    def post(self, request):
        return Response(eligibility_check(request.user, request.data))
