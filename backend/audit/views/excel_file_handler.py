import logging

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.core.exceptions import BadRequest, PermissionDenied, ValidationError
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from audit.fixtures.excel import FORM_SECTIONS, UNKNOWN_WORKBOOK
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    Audit,
    ExcelFile,
    LateChangeError,
)

from audit.intakelib.exceptions import ExcelExtractionError
from audit.models.constants import EventType
from audit.utils import FORM_SECTION_HANDLERS

from audit.context import set_audit_to_context
from dissemination.file_downloads import get_download_url, get_filename

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class ExcelFileHandlerView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    @staticmethod
    def _create_excel_file(file, audit_id, form_section):
        excel_file = ExcelFile(
            **{
                "file": file,
                "filename": "temp",
                "audit_id": audit_id,
                "form_section": form_section,
            }
        )
        excel_file.full_clean()
        return excel_file

    @staticmethod
    def _event_type(form_section):
        return {
            FORM_SECTIONS.ADDITIONAL_EINS: EventType.ADDITIONAL_EINS_UPDATED,
            FORM_SECTIONS.ADDITIONAL_UEIS: EventType.ADDITIONAL_UEIS_UPDATED,
            FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: EventType.CORRECTIVE_ACTION_PLAN_UPDATED,
            FORM_SECTIONS.FEDERAL_AWARDS: EventType.FEDERAL_AWARDS_UPDATED,
            FORM_SECTIONS.FINDINGS_TEXT: EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_UPDATED,
            FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: EventType.FINDINGS_UNIFORM_GUIDANCE_UPDATED,
            FORM_SECTIONS.NOTES_TO_SEFA: EventType.NOTES_TO_SEFA_UPDATED,
            FORM_SECTIONS.SECONDARY_AUDITORS: EventType.SECONDARY_AUDITORS_UPDATED,
        }[form_section]

    @staticmethod
    def _extract_and_validate_data(form_section, excel_file, auditee_uei):
        handler_info = FORM_SECTION_HANDLERS.get(form_section)
        if handler_info is None:
            logger.warning("No form section found with name %s", form_section)
            raise BadRequest()
        audit_data = handler_info["extractor"](excel_file.file, auditee_uei=auditee_uei)
        validator = handler_info.get("validator")
        if validator is not None and callable(validator):
            validator(audit_data)
        return audit_data

    def _save_audit_data(self, sac, form_section, audit_data, user=None):
        handler_info = FORM_SECTION_HANDLERS.get(form_section)
        if handler_info is not None:
            audit = Audit.objects.get(report_id=sac.report_id)
            audit_update = FORM_SECTION_HANDLERS.get(form_section)["audit_object"](
                audit_data
            )
            audit.audit.update(audit_update)
            audit.save(
                event_user=user,
                event_type=self._event_type(form_section),
            )

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ExcelFileHandlerView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Given a report ID and form section, redirect the caller to a download URL for the associated Excel file (if one exists)
        """
        report_id = kwargs["report_id"]
        form_section = kwargs["form_section"]

        try:
            filename = get_filename(report_id, form_section)
            download_url = get_download_url(filename)

            return redirect(download_url)
        except Audit.DoesNotExist as err:
            logger.warning("no SingleAuditChecklist found with report ID %s", report_id)
            raise PermissionDenied() from err

    def post(self, request, *_args, **kwargs):
        """
        Handle Excel file upload:
        validate Excel, validate data, verify SAC exists, redirect.
        """
        report_id = kwargs["report_id"]
        form_section = kwargs["form_section"]

        try:

            audit = Audit.objects.get(report_id=report_id)

            file = request.FILES["FILES"]

            excel_file = self._create_excel_file(file, audit.id, form_section)

            auditee_uei = audit.auditee_uei
            with set_audit_to_context(audit):
                audit_data = self._extract_and_validate_data(
                    form_section, excel_file, auditee_uei
                )
                excel_file.save(
                    event_user=request.user, event_type=self._event_type(form_section)
                )
                self._save_audit_data(audit, form_section, audit_data, request.user)

                return redirect("/")

        except Audit.DoesNotExist as err:
            logger.warning("no SingleAuditChecklist found with report ID %s", report_id)
            raise PermissionDenied() from err
        except ValidationError as err:
            # The good error, where bad rows/columns are sent back in the request.
            # These come back as tuples:
            # [(col1, row1, field1, link1, help-text1), (col2, row2, ...), ...]
            logger.warning("%s Excel upload failed validation: %s", form_section, err)
            return JsonResponse({"errors": list(err), "type": "error_row"}, status=400)
        except MultiValueDictKeyError as err:
            logger.warning("No file found in request")
            raise BadRequest() from err
        except KeyError as err:
            logger.warning("Field error. Field: %s", err)
            return JsonResponse({"errors": str(err), "type": "error_field"}, status=400)
        except ExcelExtractionError as err:
            if err.error_key == UNKNOWN_WORKBOOK:
                return JsonResponse(
                    {"errors": str(err), "type": UNKNOWN_WORKBOOK}, status=400
                )
            return JsonResponse({"errors": list(err), "type": "error_row"}, status=400)
        except LateChangeError:
            logger.warning("Attempted late change.")
            return JsonResponse(
                {
                    "errors": "Access denied. Further changes to audits that have been marked ready for certification are not permitted.",
                    "type": "no_late_changes",
                },
                status=400,
            )
