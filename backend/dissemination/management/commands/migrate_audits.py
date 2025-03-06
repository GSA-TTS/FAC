import logging

import pytz
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db import connection

from audit.intakelib.mapping_additional_eins import additional_eins_audit_view
from audit.intakelib.mapping_additional_ueis import additional_ueis_audit_view
from audit.intakelib.mapping_audit_findings import findings_audit_view
from audit.intakelib.mapping_audit_findings_text import audit_findings_text_audit_view
from audit.intakelib.mapping_corrective_action_plan import (
    corrective_action_plan_audit_view,
)
from audit.intakelib.mapping_federal_awards import federal_awards_audit_view
from audit.intakelib.mapping_notes_to_sefa import notes_to_sefa_audit_view
from audit.intakelib.mapping_secondary_auditors import secondary_auditors_audit_view
from audit.models import (
    Access,
    DeletedAccess,
    Audit,
    User,
    Schema,
    SingleAuditReportFile,
    SingleAuditChecklist,
)
from audit.models.constants import STATUS
from audit.models.utils import generate_audit_indexes
from audit.views.views import _index_awards, _index_findings, _index_general

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        queryset = SingleAuditChecklist.objects.raw(
            "select * from audit_singleauditchecklist "
            "where migrated is false "
            "order by id desc limit 50000"
        )
        paginator = Paginator(queryset, 100)  # 100 items per page

        for page_num in paginator.page_range:
            logger.info("Processing page %s", page_num)
            page = paginator.page(page_num)
            for sac in page.object_list:
                try:
                    self._migrate_sac(sac)
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"update audit_singleauditchecklist set migrated = true where report_id = '{sac.report_id}'"
                        )
                except Exception as e:
                    logger.error(f"Failed to migrate sac {sac.report_id} - {e}")
                    raise e

    @staticmethod
    def _migrate_sac(sac: SingleAuditChecklist):
        audit_data = dict()
        for idx, handler in enumerate(SAC_HANDLERS):
            audit_data.update(handler(sac))

        # update existing Audit.
        if Audit.objects.filter(report_id=sac.report_id).exists():
            Audit.objects.filter(report_id=sac.report_id).update(
                event_type="MIGRATION",
                event_user=User.objects.get(email="jason.rothacker+fac@gsa.gov"),
                audit=audit_data,
                report_id=sac.report_id,
                schema=Schema.objects.get_current_schema(audit_type="MIGRATION"),
                submission_status=sac.submission_status,
                audit_type=sac.audit_type,
            )

        # create a new Audit.
        else:
            Audit.objects.create(
                event_type="MIGRATION",
                event_user=User.objects.get(email="jason.rothacker+fac@gsa.gov"),
                audit=audit_data,
                report_id=sac.report_id,
                schema=Schema.objects.get_current_schema(audit_type="MIGRATION"),
                submission_status=sac.submission_status,
                audit_type=sac.audit_type,
            )

        audit = Audit.objects.get(report_id=sac.report_id)

        # update Access models.
        Access.objects.filter(sac__report_id=sac.report_id).update(audit=audit)
        DeletedAccess.objects.filter(sac__report_id=sac.report_id).update(audit=audit)

        # convert additional fields.
        audit.update(generate_audit_indexes(audit, sac))


def _convert_file_information(sac: SingleAuditChecklist):
    file = (
        SingleAuditReportFile.objects.filter(filename=f"{sac.report_id}.pdf")
        .order_by("date_created")
        .first()
    )
    return (
        {
            "file_information": {
                "pages": file.component_page_numbers,
                "filename": file.filename,
            }
        }
        if file is not None
        else {}
    )


def _convert_program_names(sac: SingleAuditChecklist):
    program_names = []
    if sac.federal_awards:
        awards = sac.federal_awards.get("FederalAwards", {}).get("federal_awards", [])
        for award in awards:
            program_name = award.get("program", {}).get("program_name", "")
            if program_name:
                program_names.append(program_name)

    return {"program_names": program_names} if program_names else {}


def _convert_month_year(sac: SingleAuditChecklist):
    fiscal_end = sac.general_information["auditee_fiscal_period_end"]
    # In some "in-progress" the fiscal end date is not yet set.
    if not fiscal_end:
        return {}

    audit_year, fy_end_month, _ = fiscal_end.split("-")
    return {
        "audit_year": audit_year,
        "fy_end_month": fy_end_month,
    }


def _convert_passthrough(sac: SingleAuditChecklist):
    pass_objects = []
    if sac.federal_awards:
        awards = sac.federal_awards.get("FederalAwards", {}).get("federal_awards", [])
        for award in awards:
            entities = award.get("direct_or_indirect_award", {}).get("entities", [])
            for entity in entities:
                passthrough = {
                    "award_reference": entity.get("award_reference", ""),
                    "passthrough_id": entity.get("passthrough_identifying_number", ""),
                    "passthrough_name": entity.get("passthrough_name", ""),
                }
                pass_objects.append(passthrough)

    return {"passthrough": pass_objects} if pass_objects else {}


def _convert_is_public(sac: SingleAuditChecklist):
    is_public = True
    if sac.general_information.get("user_provided_organization_type") == "tribal":
        is_public = sac.tribal_data_consent and sac.tribal_data_consent.get(
            "is_tribal_information_authorized_to_be_public"
        )

    return {"is_public": is_public}


def _convert_fac_accepted_date(sac: SingleAuditChecklist):
    date = None
    for i in range(len(sac.transition_name)):
        if sac.transition_name[i] == STATUS.SUBMITTED:
            date = sac.transition_date[i]
    submitted_date = _convert_utc_to_american_samoa_zone(date) if date else None
    return {"fac_accepted_date": submitted_date}


# Taken from Intake to Dissemination... This could be moved to a utils class
def _convert_utc_to_american_samoa_zone(date):
    us_samoa_zone = pytz.timezone("US/Samoa")
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        date = pytz.utc.localize(date)
    american_samoa_time = date.astimezone(us_samoa_zone)
    formatted_date = american_samoa_time.strftime("%Y-%m-%d")
    return formatted_date


SAC_HANDLERS = [
    lambda sac: (
        notes_to_sefa_audit_view(sac.notes_to_sefa) if sac.notes_to_sefa else {}
    ),
    lambda sac: (
        audit_findings_text_audit_view(sac.findings_text) if sac.findings_text else {}
    ),
    lambda sac: (
        additional_ueis_audit_view(sac.additional_ueis) if sac.additional_ueis else {}
    ),
    lambda sac: (
        additional_eins_audit_view(sac.additional_eins) if sac.additional_eins else {}
    ),
    lambda sac: (
        findings_audit_view(sac.findings_uniform_guidance)
        if sac.findings_uniform_guidance
        else {}
    ),
    lambda sac: (
        corrective_action_plan_audit_view(sac.corrective_action_plan)
        if sac.corrective_action_plan
        else {}
    ),
    lambda sac: (
        secondary_auditors_audit_view(sac.secondary_auditors)
        if sac.secondary_auditors
        else {}
    ),
    lambda sac: (
        federal_awards_audit_view(sac.federal_awards) if sac.federal_awards else {}
    ),
    lambda sac: {"audit_information": sac.audit_information or {}},
    lambda sac: {"general_information": sac.general_information or {}},
    lambda sac: {"auditee_certification": sac.auditee_certification or {}},
    lambda sac: {"auditor_certification": sac.auditor_certification or {}},
    lambda sac: {"tribal_data_consent": sac.tribal_data_consent or {}},
    lambda sac: {"cognizant_agency": sac.cognizant_agency},
    lambda sac: {"oversight_agency": sac.oversight_agency},
    _convert_program_names,
    _convert_file_information,
    _convert_month_year,
    _convert_passthrough,
    _convert_is_public,
    _convert_fac_accepted_date,
]
