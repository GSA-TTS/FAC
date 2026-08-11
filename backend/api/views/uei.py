import json
from rest_framework.response import Response
from rest_framework.views import APIView

from dissemination.models.general import General

from ..serializers import UEISerializer


class UEIValidationFormView(APIView):
    """
    Accepts UEI to validate and returns either a message describing the validation errors, or valid.
    """

    def post(self, request):
        data = request.data.copy()
        data["auditee_uei"] = (data.get("auditee_uei") or "").upper().strip()
        serializer = UEISerializer(data=data)

        if serializer.is_valid():
            # SAM.gov payload (stringified JSON) coming from serializer
            sam_payload = json.loads(serializer.data.get("auditee_uei"))

            # audit_year is required for the duplicate check
            audit_year = data.get("audit_year")
            if audit_year is None or str(audit_year).strip() == "":
                return Response({"valid": False, "errors": ["invalid-year"]})

            auditee_uei = data["auditee_uei"]

            # General.audit_year is a TextField, so compare as string
            duplicates = list(
                General.objects.filter(
                    auditee_uei=auditee_uei,
                    audit_year=str(audit_year),
                ).values("report_id", "auditee_name")
            )

            if duplicates:
                return Response(
                    {
                        "valid": False,
                        "errors": ["duplicate-submission"],
                        "response": {
                            **sam_payload,
                            "duplicates": duplicates,
                        },
                    }
                )

            return Response({"valid": True, "response": sam_payload})

        return Response({"valid": False, "errors": serializer.errors})
