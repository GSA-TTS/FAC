from .sac_general_lib.utils import xform_census_date_to_utc_time
from .workbooklib.post_upload_utils import record_dummy_pdf_object
from .exception_utils import (
    CrossValidationError,
    DataMigrationError,
    DataMigrationValueError,
)
from .workbooklib.workbook_builder_loader import (
    workbook_builder_loader,
)
from .workbooklib.workbook_section_handlers import (
    sections_to_handlers,
)
from .sac_general_lib.sac_creator import setup_sac
from .models import (
    ReportMigrationStatus,
    MigrationErrorDetail,
)
from audit.intake_to_dissemination import IntakeToDissemination
from audit.models import SingleAuditChecklist
from dissemination.models import (
    AdditionalEin,
    AdditionalUei,
    CapText,
    FederalAward,
    Finding,
    FindingText,
    General,
    Note,
    Passthrough,
    SecondaryAuditor,
    MigrationInspectionRecord,
)
from census_historical_migration.migration_result import MigrationResult
from .change_record import InspectionRecord

from django.core.exceptions import ValidationError
from django.utils import timezone as django_timezone

import argparse
import logging
import sys
from datetime import datetime, timezone
import traceback


logger = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
parser = argparse.ArgumentParser()


def step_through_certifications(sac, audit_header):
    sac.transition_to_ready_for_certification()
    sac.transition_to_auditor_certified()
    sac.transition_to_auditee_certified()

    sac.transition_name.append(SingleAuditChecklist.STATUS.CERTIFIED)
    sac.transition_date.append(datetime.now(timezone.utc))

    sac.transition_to_submitted()
    sac.transition_to_disseminated()

    # Patch for transition date

    submitted_date = xform_census_date_to_utc_time(audit_header.FACACCEPTEDDATE)
    auditor_certified_date = xform_census_date_to_utc_time(audit_header.CPADATESIGNED)
    auditee_certified_date = xform_census_date_to_utc_time(
        audit_header.AUDITEEDATESIGNED
    )
    patch_dates = []

    # Transition to ready for certification
    patch_dates.append(submitted_date)
    # Transition to auditor certified
    patch_dates.append(auditor_certified_date)
    # Transition to auditee certified
    patch_dates.append(auditee_certified_date)
    # Transition to certified
    patch_dates.append(submitted_date)
    # Transition to submitted
    patch_dates.append(submitted_date)
    # Transition to disseminated
    patch_dates.append(datetime.now(timezone.utc))
    sac.transition_date = patch_dates
    sac.save()


def disseminate(sac):
    logger.info("Invoking movement of data from Intake to Dissemination")
    for model in [
        AdditionalEin,
        AdditionalUei,
        CapText,
        FederalAward,
        Finding,
        FindingText,
        General,
        Note,
        Passthrough,
        SecondaryAuditor,
    ]:
        model.objects.filter(report_id=sac.report_id).delete()

    if sac.general_information:
        etl = IntakeToDissemination(sac)
        etl.load_all()
        etl.save_dissemination_objects()


def run_end_to_end(user, audit_header):
    """Attempts to migrate the given audit"""
    InspectionRecord.reset()
    try:
        sac = setup_sac(user, audit_header)
        builder_loader = workbook_builder_loader(user, sac, audit_header)

        for section, fun in sections_to_handlers.items():
            builder_loader(fun, section)

        record_dummy_pdf_object(sac, user)

        errors = sac.validate_cross()

        if errors.get("errors"):
            raise CrossValidationError(f"{errors.get('errors')}", "cross_validation")

        step_through_certifications(sac, audit_header)

        disseminate(sac)

        MigrationResult.append_success(f"{sac.report_id} created")
        record_migration_status(
            audit_header.AUDITYEAR,
            audit_header.DBKEY,
        )
        record_migration_transformations(
            audit_header.AUDITYEAR,
            audit_header.DBKEY,
            sac.report_id,
        )
    except Exception as exc:
        handle_exception(exc, audit_header)


def record_migration_transformations(audit_year, dbkey, report_id):
    """Record the transformations that were applied to the current report"""

    MigrationInspectionRecord.objects.filter(
        audit_year=audit_year, dbkey=dbkey
    ).delete()

    migration_inspection_record = MigrationInspectionRecord.objects.create(
        audit_year=audit_year,
        dbkey=dbkey,
        report_id=report_id,
    )
    migration_inspection_record.run_datetime = django_timezone.now()
    if InspectionRecord.change["general"]:
        migration_inspection_record.general = InspectionRecord.change["general"]
    if InspectionRecord.change["finding"]:
        migration_inspection_record.finding = InspectionRecord.change["finding"]
    if InspectionRecord.change["note"]:
        migration_inspection_record.note = InspectionRecord.change["note"]
    if InspectionRecord.change["federal_award"]:
        migration_inspection_record.federal_award = InspectionRecord.change[
            "federal_award"
        ]

    migration_inspection_record.save()
    InspectionRecord.reset()


def record_migration_status(audit_year, dbkey):
    """Write a migration status to the DB"""
    status = "FAILURE" if MigrationResult.has_errors() else "SUCCESS"

    ReportMigrationStatus.objects.filter(audit_year=audit_year, dbkey=dbkey).delete()

    migration_status = ReportMigrationStatus.objects.create(
        audit_year=audit_year,
        dbkey=dbkey,
        run_datetime=django_timezone.now(),
        migration_status=status,
    )
    migration_status.save()

    return migration_status


def record_migration_error(status, tag, exc_type, message):
    """Write a migration error to the DB"""
    MigrationErrorDetail(
        report_migration_status=status,
        tag=tag,
        exception_class=exc_type,
        detail=message,
    ).save()


def handle_exception(exc, audit_header):
    """Handles exceptions encountered during run_end_to_end()"""
    try:
        tag = exc.tag
    except Exception:
        tag = "exception"

    try:
        message = exc.message
    except Exception:
        message = str(exc)

    exc_type = type(exc)
    if exc_type == DataMigrationValueError:
        logger.error(f"DataMigrationValueError: {message}")
        tag = tag or "unexpected_value"
    elif exc_type == DataMigrationError:
        logger.error(f"DataMigrationError: {message}")
        tag = tag or "data_migration"
    elif exc_type == ValidationError:
        logger.error(f"ValidationError: {message}")
        tag = "schema_validation"
    else:
        logger.error(f"Unexpected error type {exc_type}: {message}")

        tb = traceback.extract_tb(sys.exc_info()[2])
        for frame in tb:
            logger.error(f"{frame.filename}:{frame.lineno} {frame.name}: {frame.line}")

    MigrationResult.append_error(f"{exc}")

    status = record_migration_status(
        audit_header.AUDITYEAR,
        audit_header.DBKEY,
    )

    record_migration_error(
        status,
        tag,
        exc_type.__name__,
        message,
    )
