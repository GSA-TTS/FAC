import json
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import UEISerializer


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
