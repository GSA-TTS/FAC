from django.urls import reverse

from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import EligibilitySerializer


def eligibility_check(user, data):
    serializer = EligibilitySerializer(data=data)
    if serializer.is_valid():
        next_step = reverse("api-auditee-info")

        # Store step 0 data in profile, overwriting any pre-existing.
        user.profile.entry_form_data = serializer.data
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
