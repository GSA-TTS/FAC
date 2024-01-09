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
    MigrationChangeRecord,
)
from census_historical_migration.migration_result import MigrationResult
from .change_record import ChangeRecord

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone as django_timezone

import argparse
import logging
import sys
import math
import os
import jwt
import requests
from datetime import datetime, timezone
import traceback


logger = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
parser = argparse.ArgumentParser()


def step_through_certifications(sac):
    sac.transition_to_ready_for_certification()
    sac.transition_to_auditor_certified()
    sac.transition_to_auditee_certified()

    # FIXME-MSHD: We have no method transition_to_certified()
    sac.transition_name.append(SingleAuditChecklist.STATUS.CERTIFIED)
    sac.transition_date.append(datetime.now(timezone.utc))

    sac.transition_to_submitted()
    sac.transition_to_disseminated()
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


def create_payload(api_url, role="api_fac_gov"):
    payload = {
        # PostgREST only cares about the role.
        "role": role,
        "created": datetime.today().isoformat(),
    }
    return payload


def call_api(api_url, endpoint, rid, field):
    # We must pass a properly signed JWT to access the API
    encoded_jwt = jwt.encode(
        create_payload(api_url), os.getenv("PGRST_JWT_SECRET"), algorithm="HS256"
    )
    full_request = f"{api_url}/{endpoint}?report_id=eq.{rid}&select={field}"
    response = requests.get(
        full_request,
        headers={
            "Authorization": f"Bearer {encoded_jwt}",
            "X-Api-Key": os.getenv("CYPRESS_API_GOV_KEY"),
        },
        timeout=10,
    )
    return response


def just_numbers(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def are_they_both_none_or_empty(a, b):
    a_val = True if (a is None or a == "") else False
    b_val = True if (b is None or b == "") else False
    return a_val and b_val


def check_equality(in_wb, in_api):
    # Type requirement is sometimes just 'N'
    if in_wb in ["Y", "N"] and isinstance(in_api, bool):
        return (True if in_wb == "Y" else False) == in_api
    elif just_numbers(in_wb) and just_numbers(in_api):
        return (
            True if math.isclose(float(in_wb), float(in_api), rel_tol=1e-1) else False
        )
    elif isinstance(in_wb, str) and isinstance(in_api, str):
        return _compare_multiline_strings(in_wb, in_api)
    elif in_wb is None or in_api is None:
        return are_they_both_none_or_empty(in_wb, in_api)
    else:
        return str(in_wb) == str(in_api)


def _compare_multiline_strings(str1, str2):
    """Compare two multiline strings."""

    lines1 = [line.strip() for line in str1.splitlines()]
    lines2 = [line.strip() for line in str2.splitlines()]

    # Compare line counts
    if len(lines1) != len(lines2):
        logger.info("Line count differs.")
        return False

    # Compare each line
    for index, (line1, line2) in enumerate(zip(lines1, lines2)):
        if line1 != line2:
            logger.info(
                f"Difference found on line {index + 1}:\n- {repr(line1)}\n- {repr(line2)}"
            )
            return False

    return True


def get_api_values(endpoint, rid, field):
    api_url = settings.POSTGREST.get(settings.ENVIRONMENT)
    res = call_api(api_url, endpoint, rid, field)

    if res.status_code == 200:
        # logger.info(f'{res.status_code} {res.url} {res.json()}')
        return list(map(lambda d: d[field], res.json()))
    else:
        logger.error(f"{res.status_code} {res.url}")
        return []


def count(d, key):
    if key in d:
        d[key] += 1
    else:
        d[key] = 1


def combine_counts(combined, d):
    for k in combined.keys():
        if k in d:
            combined[k] = combined[k] + d[k]
    return combined


def process_singletons(endo, summary):
    """Process the singletons in the JSON test table"""
    for field, value in endo.get("singletons", {}).items():
        api_values = get_api_values(endo["endpoint"], endo["report_id"], field)
        eq = check_equality(value, api_values[0])
        if eq:
            count(summary, "correct_fields")
        else:
            logger.info(
                f"Does not match. [eq {eq}] [field {field}] [field val {value}] != [api val {api_values[0]}]"
            )
            count(summary, "incorrect_fields")


def process_rows(endo, combined_summary, summary):
    """Process the rows in the JSON test table"""
    rows = endo.get("rows", [])
    equality_results = []
    for row_ndx, row in enumerate(rows):
        count(summary, "total_rows")

        if False in equality_results:
            count(combined_summary, "incorrect_rows")
        else:
            count(combined_summary, "correct_rows")

        equality_results = []

        for field_ndx, f in enumerate(row["fields"]):
            # logger.info(f"Checking /{endo["endpoint"]} {endo["report_id"]} {f}")
            # logger.info(f"{get_api_values(endo["endpoint"], endo["report_id"], f)}")
            api_values = get_api_values(endo["endpoint"], endo["report_id"], f)
            this_api_value = api_values[row_ndx]
            if field_ndx < len(row["values"]):
                this_field_value = row["values"][field_ndx]
                eq = check_equality(this_field_value, this_api_value)
                if not eq:
                    logger.info(
                        f"Does not match. [eq {eq}] [field {f}] [field val {this_field_value}] != [api val {this_api_value}]"
                    )
                equality_results.append(eq)
            else:
                # Log a message if field_ndx does not exist
                logger.info(
                    f"Index {field_ndx} out of range for 'values' in row. Max index is {len(row['values']) - 1}"
                )
                logger.info(
                    f"Field '{f}' with value '{this_api_value}' at index '{field_ndx}' is missing from test tables 'values'."
                )

        if all(equality_results):
            count(summary, "correct_fields")
        else:
            count(summary, "incorrect_fields")


def api_check(json_test_tables):
    combined_summary = {"endpoints": 0, "correct_rows": 0, "incorrect_rows": 0}

    for endo in json_test_tables:
        count(combined_summary, "endpoints")
        endpoint = endo["endpoint"]
        summary = {}

        logger.info(f"-------------------- {endpoint} --------------------")
        process_singletons(endo, summary)
        process_rows(endo, combined_summary, summary)

        logger.info(summary)
        combined_summary = combine_counts(combined_summary, summary)

    return combined_summary


def run_end_to_end(user, audit_header):
    """Attempts to migrate the given audit"""
    ChangeRecord.reset()
    try:
        sac, gen_api_data = setup_sac(user, audit_header)

        if sac.general_information["audit_type"] == "alternative-compliance-engagement":
            logger.info(
                f"Skipping ACE audit: {audit_header.DBKEY} {audit_header.AUDITYEAR}"
            )
            raise DataMigrationError(
                "Skipping ACE audit",
                "skip_ace_audit",
            )
        else:
            builder_loader = workbook_builder_loader(user, sac, audit_header)
            json_test_tables = []

            for section, fun in sections_to_handlers.items():
                # FIXME: Can we conditionally upload the addl' and secondary workbooks?
                (_, json, _) = builder_loader(fun, section)
                json_test_tables.append(json)

            # Append total amount expended to general table checker
            gen_api_data["singletons"]["total_amount_expended"] = sac.federal_awards[
                "FederalAwards"
            ]["total_amount_expended"]

            json_test_tables.append(gen_api_data)

            record_dummy_pdf_object(sac, user)

            errors = sac.validate_cross()

            if errors.get("errors"):
                raise CrossValidationError(
                    f"{errors.get('errors')}", "cross_validation"
                )

            step_through_certifications(sac)

            disseminate(sac)
            combined_summary = api_check(json_test_tables)
            logger.info(combined_summary)
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
    migration_change_record, created = MigrationChangeRecord.objects.get_or_create(
        audit_year=audit_year,
        dbkey=dbkey,
        report_id=report_id,
    )
    migration_change_record.run_datetime = django_timezone.now()
    if ChangeRecord.change["general"]:
        migration_change_record.general = ChangeRecord.change["general"]
    if ChangeRecord.change["finding"]:
        migration_change_record.finding = ChangeRecord.change["finding"]
    if ChangeRecord.change["note"]:
        migration_change_record.note = ChangeRecord.change["note"]
    if ChangeRecord.change["federal_award"]:
        migration_change_record.federal_award = ChangeRecord.change["federal_award"]

    migration_change_record.save()
    ChangeRecord.reset()


def record_migration_status(audit_year, dbkey):
    """Write a migration status to the DB"""
    status = "FAILURE" if MigrationResult.has_errors() else "SUCCESS"

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
