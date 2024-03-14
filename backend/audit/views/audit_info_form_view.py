import logging
from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from audit.forms import AuditInfoForm
from audit.mixins import SingleAuditChecklistAccessRequiredMixin
from audit.models import SingleAuditChecklist, SubmissionEvent
from audit.validators import validate_audit_information_json
from config.settings import (
    AGENCY_NAMES,
    GAAP_RESULTS,
    SP_FRAMEWORK_BASIS,
    SP_FRAMEWORK_OPINIONS,
)

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class AuditInfoFormView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            current_info = {}
            if sac.audit_information:
                current_info = {
                    "cleaned_data": {
                        "gaap_results": sac.audit_information.get("gaap_results"),
                        "sp_framework_basis": sac.audit_information.get(
                            "sp_framework_basis"
                        ),
                        "is_sp_framework_required": sac.audit_information.get(
                            "is_sp_framework_required"
                        ),
                        "sp_framework_opinions": sac.audit_information.get(
                            "sp_framework_opinions"
                        ),
                        "is_going_concern_included": sac.audit_information.get(
                            "is_going_concern_included"
                        ),
                        "is_internal_control_deficiency_disclosed": sac.audit_information.get(
                            "is_internal_control_deficiency_disclosed"
                        ),
                        "is_internal_control_material_weakness_disclosed": sac.audit_information.get(
                            "is_internal_control_material_weakness_disclosed"
                        ),
                        "is_material_noncompliance_disclosed": sac.audit_information.get(
                            "is_material_noncompliance_disclosed"
                        ),
                        "is_aicpa_audit_guide_included": sac.audit_information.get(
                            "is_aicpa_audit_guide_included"
                        ),
                        "dollar_threshold": sac.audit_information.get(
                            "dollar_threshold"
                        ),
                        "is_low_risk_auditee": sac.audit_information.get(
                            "is_low_risk_auditee"
                        ),
                        "agencies": sac.audit_information.get("agencies"),
                    }
                }

            context = self._get_context(sac, current_info)

            return render(request, "audit/audit-info-form.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
        except Exception as e:
            logger.info("Unexpected error in AuditInfoFormView get.\n%s", e)
            raise BadRequest()

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form = AuditInfoForm(request.POST)

            if form.is_valid():
                form.clean_booleans()
                # List of keys to delete if "not_gaap" not in form.cleaned_data["gaap_results"]
                keys_to_delete = [
                    "sp_framework_basis",
                    "is_sp_framework_required",
                    "sp_framework_opinions",
                ]

                if "not_gaap" not in form.cleaned_data["gaap_results"]:
                    for key in keys_to_delete:
                        form.cleaned_data.pop(key, None)

                validated = validate_audit_information_json(form.cleaned_data)

                sac.audit_information = validated
                sac.save(
                    event_user=request.user,
                    event_type=SubmissionEvent.EventType.AUDIT_INFORMATION_UPDATED,
                )
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        logger.warn(f"ERROR in field {field} : {error}")

                form.clean_booleans()
                context = self._get_context(sac, form)
                return render(request, "audit/audit-info-form.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
        except Exception as e:
            logger.info("Enexpected error in AuditInfoFormView post.\n%s", e)
            raise BadRequest()

    def _get_context(self, sac, form):
        context = {
            "auditee_name": sac.auditee_name,
            "report_id": sac.report_id,
            "auditee_uei": sac.auditee_uei,
            "user_provided_organization_type": sac.user_provided_organization_type,
            "agency_names": AGENCY_NAMES,
            "gaap_results": GAAP_RESULTS,
            "sp_framework_basis": SP_FRAMEWORK_BASIS,
            "sp_framework_opinions": SP_FRAMEWORK_OPINIONS,
        }
        for field, value in context.items():
            logger.warn(f"{field}:{value}")
        context.update(
            {
                "form": form,
            }
        )
        return context
