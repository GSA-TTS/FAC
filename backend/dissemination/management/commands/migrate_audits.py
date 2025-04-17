# README

# When testing this script, make sure you proceed through the following:
# 1. Make sure you import the public prod data dump from the drive into your local DB.
# 2. If you have already migrated some audits and want to reset to a clean slate,
#    run these SQL queries in order:
#    - DELETE FROM public.audit_history WHERE event='MIGRATION';
#    - UPDATE public.audit_access SET audit_id=null;
#    - UPDATE public.audit_deletedaccess SET audit_id=null;
#    - UPDATE public.audit_submissionevent SET audit_id=null;
#    - UPDATE public.audit_singleauditchecklist SET migrated_to_audit=false;
#    - DELETE FROM public.audit_audit;
# 3. Run the command in a separate shell from the app.
#    - If you want to ONLY target disseminated records, pass the parameter "--disseminated".
#    - If you want to ONLY target intake records, pass the parameter "--intake".
#    - If you want to target ALL records, leave out the parameters.

import logging
import time

from django.core.management.base import BaseCommand
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
    Audit,
    AuditValidationWaiver,
    DeletedAccess,
    ExcelFile,
    SacValidationWaiver,
    SingleAuditReportFile,
    SingleAuditChecklist,
    SubmissionEvent,
    User,
)
from audit.models.history import History
from audit.models.constants import STATUS
from audit.models.utils import (
    generate_audit_indexes,
    convert_utc_to_american_samoa_zone,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "--disseminated",
            action="store_true",
            help="Migrates the Audit model to disseminated records.",
        )
        parser.add_argument(
            "--intake",
            action="store_true",
            help="Migrates the Audit model to in_progress records.",
        )
        parser.add_argument(
            "--report_id",
            type=str,
            help="Migrate a specific SingleAuditChecklist by ID.",
        )

    def handle(self, *args, **kwargs):

        BATCH_SIZE = 100

        # iterate through unmigrated SACs.
        queryset = _get_query(kwargs, BATCH_SIZE)
        total = _get_query(kwargs, None).count()
        count = 0
        logger.info(f"Found {total} records to parse through.")
        logger.info(
            f"Selected {queryset.count()} records for the first batch of migrations."
        )
        
        while queryset.count() != 0:
            t_migrate_sac = 0
            t_update_flag = 0
            t_get_batch = 0

            self.t_audit = 0
            self.t_create = 0
            self.t_access = 0
            self.t_indexes = 0
            self.t_save = 0
            self.t_history = 0
            self.t_files = 0
            self.t_waivers = 0

            accesses = Access.objects.filter(sac__report_id__in=queryset.values('report_id'))
            deletedaccesses = DeletedAccess.objects.filter(sac__report_id__in=queryset.values('report_id'))
            submissionevents = SubmissionEvent.objects.filter(sac__id__in=queryset.values('id'))
            sars = SingleAuditReportFile.objects.filter(sac__id__in=queryset.values('id'))
            excels = ExcelFile.objects.filter(sac__id__in=queryset.values('id'))
            validations = SacValidationWaiver.objects.filter(report_id__in=queryset.values('report_id'))
            for sac in queryset:
                try:
                    t0 = time.monotonic()
                    self._migrate_sac(
                        self,
                        sac,
                        accesses,
                        deletedaccesses,
                        submissionevents,
                        sars,
                        excels,
                        validations
                    )
                    t_migrate_sac += time.monotonic() - t0

                    t0 = time.monotonic()
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"update audit_singleauditchecklist set migrated_to_audit = true where report_id = '{sac.report_id}'"
                        )
                    t_update_flag += time.monotonic() - t0
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to migrate sac {sac.report_id} - {e}")
                    raise e
            logger.info(
                f"Migration progress... ({count} / {total}) ({(count / total) * 100}%)"
            )
            t0 = time.monotonic()
            queryset = _get_query(kwargs, BATCH_SIZE)
            t_get_batch += time.monotonic() - t0
            print(f" - Time to migrate batch of 100          - {t_migrate_sac}")
            print(f"    - Audit info - {self.t_audit}")
            print(f"    - Creation   - {self.t_create}")
            print(f"    - Access     - {self.t_access}")
            print(f"    - Indexes    - {self.t_indexes}")
            print(f"    - Re-saving  - {self.t_save}")
            print(f"    - History    - {self.t_history}")
            print(f"    - Files      - {self.t_files}")
            print(f"    - Waivers    - {self.t_waivers}")
            print(f" - Time to mark batch of 100 as migrated - {t_update_flag}")
            print(f" - Time to query next batch              - {t_get_batch}")

        logger.info("Completed audit migrations.")

    @staticmethod
    def _migrate_sac(self, sac: SingleAuditChecklist, accesses: Access, deletedaccesses: DeletedAccess, submissionevents: SubmissionEvent, sars: SingleAuditReportFile, excels: ExcelFile, validations: SacValidationWaiver):
        t1 = time.monotonic()
        audit_data = dict()
        for idx, handler in enumerate(SAC_HANDLERS):
            audit_data.update(handler(sac))
        self.t_audit += time.monotonic() - t1
        
        # create the audit.
        if not Audit.objects.filter(report_id=sac.report_id).exists():
            t1 = time.monotonic()
            audit = Audit.objects.create(
                event_type="MIGRATION",
                data_source=sac.data_source,
                # FOR DEBUGGING
                # Change the email to your local user (make sure you login once after app startup).
                event_user=get_or_create_sot_migration_user(),
                created_by=sac.submitted_by,
                audit=audit_data,
                report_id=sac.report_id,
                submission_status=sac.submission_status,
                audit_type=sac.audit_type,
            )

            if sac.date_created:
                audit.created_at = sac.date_created
            self.t_create += time.monotonic() - t1

            # update Access models.
            t1 = time.monotonic()
            accesses.filter(sac__report_id=sac.report_id).update(audit=audit)
            deletedaccesses.filter(sac__report_id=sac.report_id).update(
                audit=audit
            )
            self.t_access += time.monotonic() - t1

            # convert additional fields.
            t1 = time.monotonic()
            if sac.submission_status == STATUS.DISSEMINATED:
                audit.audit.update(generate_audit_indexes(audit))

                # re-adjust cog/over afterwards.
                audit.cognizant_agency = sac.cognizant_agency
                audit.oversight_agency = sac.oversight_agency
                audit.audit["cognizant_agency"] = sac.cognizant_agency
                audit.audit["oversight_agency"] = sac.oversight_agency
            self.t_indexes += time.monotonic() - t1

            t1 = time.monotonic()
            audit.save()
            self.t_save += time.monotonic() - t1

            # copy SubmissionEvents into History records.
            t1 = time.monotonic()
            events = submissionevents.filter(sac=sac)
            for event in events:
                history = History.objects.create(
                    event=event.event,
                    report_id=sac.report_id,
                    event_data=audit.audit,
                    version=0,
                    updated_by=event.user,
                )
                history.updated_at = event.timestamp
                history.save()
            self.t_history += time.monotonic() - t1

            # assign audit reference to file-based models.
            t1 = time.monotonic()
            sars.filter(sac=sac).update(audit=audit)
            excels.filter(sac=sac).update(audit=audit)
            self.t_files += time.monotonic() - t1

            # copy SacValidationWaivers.
            t1 = time.monotonic()
            if not AuditValidationWaiver.objects.filter(
                report_id=sac.report_id
            ).exists():
                waivers = validations.filter(report_id=sac.report_id)
                for waiver in waivers:
                    AuditValidationWaiver.objects.create(
                        report_id=sac.report_id,
                        timestamp=waiver.timestamp,
                        approver_email=waiver.approver_email,
                        approver_name=waiver.approver_name,
                        requester_email=waiver.requester_email,
                        requester_name=waiver.requester_name,
                        justification=waiver.justification,
                        waiver_types=waiver.waiver_types,
                    )
            self.t_waivers += time.monotonic() - t1


def _get_query(kwargs, max_records):
    """Fetch unmigrated SACs, based on parameters."""
    if kwargs.get("report_id"):
        queryset = SingleAuditChecklist.objects.filter(
            migrated_to_audit=False, report_id=kwargs.get("report_id")
        )
    elif kwargs.get("disseminated"):
        queryset = SingleAuditChecklist.objects.filter(
            migrated_to_audit=False, submission_status="disseminated"
        )
    elif kwargs.get("intake"):
        queryset = SingleAuditChecklist.objects.filter(migrated_to_audit=False).exclude(
            submission_status="disseminated"
        )
    else:
        queryset = SingleAuditChecklist.objects.filter(migrated_to_audit=False)

    # only return up to "max_records" if applied.
    if max_records:
        return queryset[:max_records]
    else:
        return queryset


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
                    "award_reference": award.get("award_reference", ""),
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
    submitted_date = convert_utc_to_american_samoa_zone(date) if date else None
    return {"fac_accepted_date": submitted_date}


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
    lambda sac: {"type_audit_code": "UG"},
    _convert_program_names,
    _convert_file_information,
    _convert_month_year,
    _convert_passthrough,
    _convert_is_public,
    _convert_fac_accepted_date,
]


def get_or_create_sot_migration_user():
    """Returns the default migration user"""
    user_email = "fac-sot-migration-auditee-official@fac.gsa.gov"
    user_name = "fac-sot-migration-auditee-official"
    user = None

    users = User.objects.filter(email=user_email)
    if users:
        user = users.first()
    else:
        logger.info("Creating user %s %s", user_email, user_name)
        user = User(username=user_name, email=user_email)
        user.save()

    return user
