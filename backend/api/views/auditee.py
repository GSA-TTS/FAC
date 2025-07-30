from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import AuditeeInfoSerializer


def auditee_info_check(user, data):
    serializer = AuditeeInfoSerializer(data=data)

    if serializer.is_valid():
        next_step = reverse("api-eligibility")

        # Store step 1 data in profile, combined with the existing.
        user.profile.entry_form_data = user.profile.entry_form_data | data
        user.profile.save()
        return {"info_check_passed": True, "next": next_step}

    return {"info_check_passed": False, "errors": serializer.errors}


class AuditeeInfoView(APIView):
    """
    Accepts information from Step 2 (Auditee information) of the "Create New Audit"
    pre-SAC checklist. It saves the information to the user profile and returns either
    messages describing missing info or a reference to the next step to advance to.
    """

    def post(self, request):
        return Response(auditee_info_check(request.user, request.data))
