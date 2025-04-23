# README

# When testing this script, make sure you proceed through the following:
# 1. Make sure you import the public prod data dump from the drive into your local DB.
# 2. If you have already migrated some audits and want to reset to a clean slate,
#    run these SQL queries in order:
#    - DELETE FROM public.audit_history WHERE event='sot_migration';
#    - UPDATE public.audit_access SET audit_id=null;
#    - UPDATE public.audit_deletedaccess SET audit_id=null;
#    - UPDATE public.audit_submissionevent SET audit_id=null;
#    - UPDATE public.audit_singleauditchecklist SET migrated_to_audit=false;
#    - DELETE FROM public.audit_audit;
# 3. Run the command in a separate shell from the app.
#    - If you want to ONLY target disseminated records, pass the parameter "--disseminated".
#    - If you want to ONLY target intake records, pass the parameter "--intake".
#    - If you want to target ALL records, leave out the parameters.

from datetime import datetime
import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction

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
        migration_user = get_or_create_sot_migration_user()
        logger.info("Starting migration...")

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

            for sac in queryset.iterator():
                try:
                    t0 = time.monotonic()
                    self._migrate_sac(self, migration_user, sac)
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
            del queryset
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
    def _migrate_sac(self, migration_user: User, sac: SingleAuditChecklist):
        with transaction.atomic():
            t1 = time.monotonic()
            audit_data = dict()
            for idx, handler in enumerate(SAC_HANDLERS):
                audit_data.update(handler(sac))

            # convert file information.
            audit_data.update(_convert_file_information(sac))
            self.t_audit += time.monotonic() - t1

            # create the audit.
            t1 = time.monotonic()
            audit = Audit.objects.create(
                event_type=STATUS.SOURCE_OF_TRUTH_MIGRATION,
                data_source=sac.data_source,
                event_user=migration_user,
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
            Access.objects.filter(sac=sac).update(audit=audit)
            DeletedAccess.objects.filter(sac=sac).update(audit=audit)
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
            events = SubmissionEvent.objects.filter(sac=sac).values(
                "event", "timestamp", "user__id"
            )
            histories = [
                History(
                    event=event["event"],
                    report_id=sac.report_id,
                    event_data={},
                    version=0,
                    updated_by_id=event["user__id"],
                )
                for event in events
            ]
            History.objects.bulk_create(histories, batch_size=25)

            for history, event in zip(histories, events):
                history.updated_at = event["timestamp"]

            # Step 3: Bulk update
            History.objects.bulk_update(histories, ["updated_at"])
            if sac.data_source == settings.CENSUS_DATA_SOURCE and not histories:
                extra_histories = create_history_objects(
                    transition_name=sac.transition_name,
                    transition_date=sac.transition_date,
                    report_id=sac.report_id,
                    user=migration_user,
                )
                # Extract updated_at values separately
                updated_at_map = [h.updated_at for h in extra_histories]

                # Step 1: Temporarily reset updated_at (so it's overwritten later)
                for h in extra_histories:
                    h.updated_at = None
                History.objects.bulk_create(extra_histories, batch_size=25)
                # Step 3: Re-assign updated_at and bulk update
                for h, new_time in zip(extra_histories, updated_at_map):
                    h.updated_at = new_time
                History.objects.bulk_update(extra_histories, ["updated_at"])
            self.t_history += time.monotonic() - t1

            # assign audit reference to file-based models.
            t1 = time.monotonic()
            SingleAuditReportFile.objects.filter(sac=sac).update(audit=audit)
            ExcelFile.objects.filter(sac=sac).update(audit=audit)
            self.t_files += time.monotonic() - t1

            # copy SacValidationWaivers.
            t1 = time.monotonic()
            sac_waivers = SacValidationWaiver.objects.filter(
                report_id=sac.report_id
            ).values(
                "timestamp",
                "approver_email",
                "approver_name",
                "requester_email",
                "requester_name",
                "justification",
                "waiver_types",
            )
            audit_waivers = [
                AuditValidationWaiver(
                    report_id=audit,
                    timestamp=waiver["timestamp"],
                    approver_email=waiver["approver_email"],
                    approver_name=waiver["approver_name"],
                    requester_email=waiver["requester_email"],
                    requester_name=waiver["requester_name"],
                    justification=waiver["justification"],
                    waiver_types=waiver["waiver_types"],
                )
                for waiver in sac_waivers
            ]
            AuditValidationWaiver.objects.bulk_create(audit_waivers)
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

    # exclude SACs that have already migrated with an Audit.
    queryset = queryset.exclude(report_id__in=Audit.objects.all().values("report_id"))

    # only return up to "max_records" if applied.
    if max_records:
        return queryset[:max_records]
    else:
        return queryset


def _convert_file_information(sac: SingleAuditChecklist):
    try:
        file = SingleAuditReportFile.objects.filter(sac=sac).latest("date_created")
        return {
            "file_information": {
                "pages": file.component_page_numbers,
                "filename": file.filename,
            }
        }
    except SingleAuditReportFile.DoesNotExist:
        return {}


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
    _convert_month_year,
    _convert_passthrough,
    _convert_is_public,
    _convert_fac_accepted_date,
]


def get_or_create_sot_migration_user():
    """Returns the default migration user"""
    user_email = "fac-sot-migration-auditee-official@fac.gsa.gov"
    user_name = "fac-sot-migration-auditee-official"
    my_user = None

    users = User.objects.filter(email=user_email)
    if users:
        my_user = users.first()
    else:
        logger.info("Creating user %s %s", user_email, user_name)
        my_user = User(username=user_name, email=user_email)
        my_user.save()

    return my_user


STATUS_TO_EVENT = {
    STATUS.READY_FOR_CERTIFICATION: SubmissionEvent.EventType.LOCKED_FOR_CERTIFICATION,
    STATUS.AUDITOR_CERTIFIED: SubmissionEvent.EventType.AUDITOR_CERTIFICATION_COMPLETED,
    STATUS.AUDITEE_CERTIFIED: SubmissionEvent.EventType.AUDITEE_CERTIFICATION_COMPLETED,
    STATUS.SUBMITTED: SubmissionEvent.EventType.SUBMITTED,
    STATUS.DISSEMINATED: SubmissionEvent.EventType.DISSEMINATED,
}


def create_history_objects(
    transition_name: list[str],
    transition_date: list[str],
    report_id: str,
    user: any,
) -> list[History]:

    transitions = []
    for name, date_val in zip(transition_name, transition_date):
        if isinstance(date_val, str):
            try:
                dt = datetime.strptime(date_val.split(".")[0], "%Y-%m-%d %H:%M:%S%z")
            except ValueError:
                dt = datetime.strptime(date_val, "%Y-%m-%d %H:%M:%S%z")
        else:
            dt = date_val
        transitions.append((name, dt))

    # Only grab the most recent transition per status
    latest_transitions = {}
    for name, dt in transitions:
        if name not in latest_transitions or dt > latest_transitions[name]:
            latest_transitions[name] = dt

    history_objects = []
    for status, dt in latest_transitions.items():
        event = STATUS_TO_EVENT.get(status)
        if not event:
            continue  # not all status match an event type
        history = History(
            event=event,
            report_id=report_id,
            version=0,
            event_data={},
            updated_at=dt,
            updated_by=user,
        )
        history_objects.append(history)

    return history_objects
