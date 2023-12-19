from ..exception_utils import (
    DataMigrationError,
    DataMigrationValueError,
)
from ..workbooklib.workbook_builder_loader import (
    workbook_builder_loader,
)
from ..workbooklib.workbook_section_handlers import (
    sections_to_handlers,
)
from ..workbooklib.post_upload_utils import _post_upload_pdf
from ..sac_general_lib.sac_creator import setup_sac
from ..models import (
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
)

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
    stati = [
        SingleAuditChecklist.STATUS.IN_PROGRESS,
        SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION,
        SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED,
        SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED,
        SingleAuditChecklist.STATUS.CERTIFIED,
        SingleAuditChecklist.STATUS.SUBMITTED,
        SingleAuditChecklist.STATUS.DISSEMINATED,
    ]
    for status in stati:
        sac.transition_name.append(status)
        sac.transition_date.append(datetime.now(timezone.utc))
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


def check_equality(in_wb, in_json):
    # Type requirement is sometimes just 'N'
    if in_wb in ["Y", "N"] and isinstance(in_json, bool):
        return (True if in_wb == "Y" else False) == in_json
    elif just_numbers(in_wb) and just_numbers(in_json):
        return (
            True if math.isclose(float(in_wb), float(in_json), rel_tol=1e-1) else False
        )
    elif isinstance(in_wb, str) and isinstance(in_json, str):
        return _compare_multiline_strings(in_wb, in_json)
    elif in_wb is None or in_json is None:
        return are_they_both_none_or_empty(in_wb, in_json)
    else:
        return in_wb == in_json


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


def api_check(json_test_tables):
    combined_summary = {"endpoints": 0, "correct_rows": 0, "incorrect_rows": 0}

    for endo in json_test_tables:
        count(combined_summary, "endpoints")
        endpoint = endo["endpoint"]
        report_id = endo["report_id"]
        summary = {}
        equality_results = []

        logger.info(f"-------------------- {endpoint} --------------------")

        for row_ndx, row in enumerate(endo["rows"]):
            count(summary, "total_rows")

            if False in equality_results:
                count(combined_summary, "incorrect_rows")
            else:
                count(combined_summary, "correct_rows")

            equality_results = []

            for field_ndx, f in enumerate(row["fields"]):
                # logger.info(f"Checking /{endpoint} {report_id} {f}")
                # logger.info(f"{get_api_values(endpoint, report_id, f)}")
                api_values = get_api_values(endpoint, report_id, f)
                this_api_value = api_values[row_ndx]

                # Check if field_ndx exists in row["values"]
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

        logger.info(summary)
        combined_summary = combine_counts(combined_summary, summary)

    return combined_summary


def run_end_to_end(user, audit_header, result):
    """Attempts to migrate the given audit"""
    try:
        sac = setup_sac(user, audit_header)

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

            _post_upload_pdf(sac, user, "audit/fixtures/basic.pdf")
            step_through_certifications(sac)

            errors = sac.validate_cross()
            if errors.get("errors"):
                result["errors"].append(f"{errors.get('errors')}")
                return

            disseminate(sac)
            combined_summary = api_check(json_test_tables)
            logger.info(combined_summary)
            result["success"].append(f"{sac.report_id} created")
    except Exception as exc:
        handle_exception(exc, audit_header, result)
    else:
        record_migration_status(
            audit_header.AUDITYEAR,
            audit_header.DBKEY,
            len(result["errors"]) > 0,
        )


def record_migration_status(audit_year, dbkey, has_failed):
    """Write a migration status to the DB"""
    status = "FAILURE" if has_failed else "SUCCESS"

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


def handle_exception(exc, audit_header, result):
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

    result["errors"].append(f"{exc}")

    status = record_migration_status(
        audit_header.AUDITYEAR,
        audit_header.DBKEY,
        True,
    )

    record_migration_error(
        status,
        tag,
        exc_type.__name__,
        message,
    )
