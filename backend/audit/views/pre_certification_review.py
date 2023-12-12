from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views import generic
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import SingleAuditChecklist
from audit.intake_to_dissemination import IntakeToDissemination


class PreCertificationReview(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, report_id):
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            intake_to_dissem = IntakeToDissemination(
                sac, mode=IntakeToDissemination.PRE_CERTIFICATION_REVIEW
            )
            i2d_data = intake_to_dissem.load_all()

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "general": i2d_data["Generals"][0],
                "data": self.dissemination_to_audit_data(i2d_data),
            }

            return render(
                request,
                "audit/pre-certification-review.html",
                context,
            )
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def dissemination_to_audit_data(self, i2d_data):
        i2d_to_pretty = {
            "SecondaryAuditors": "Secondary Auditors",
            "FederalAwards": "Awards",
            "Findings": "Audit Findings",
            "FindingTexts": "Audit Findings Text",
            "Passthroughs": "Passthroughs",
            "CapTexts": "Corrective Action Plan",
            "Notes": "Notes to SEFA",
            "AdditionalUEIs": "Additional UEIs",
            "AdditionalEINs": "Additional EINs",
        }

        data = {}

        for name_i2d, name_pretty in i2d_to_pretty.items():
            data[name_pretty] = i2d_data.get(name_i2d)

        return data
