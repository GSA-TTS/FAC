from census_historical_migration.exception_utils import DataMigrationError
from users.models import User
import argparse
import logging
import sys
import math
from config import settings
import os
import jwt
import requests
from pprint import pprint
from datetime import datetime
import traceback

from census_historical_migration.workbooklib.workbook_builder_loader import (
    workbook_builder_loader,
)
from census_historical_migration.sac_general_lib.sac_creator import setup_sac
from census_historical_migration.workbooklib.workbook_section_handlers import (
    sections_to_handlers,
)
from census_historical_migration.workbooklib.post_upload_utils import _post_upload_pdf
from audit.intake_to_dissemination import IntakeToDissemination

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

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
parser = argparse.ArgumentParser()

# Peewee runs a really noisy DEBUG log.
pw = logging.getLogger("peewee")
pw.addHandler(logging.StreamHandler())
pw.setLevel(logging.INFO)


def step_through_certifications(sac):
    sac.transition_to_ready_for_certification()
    sac.transition_to_auditor_certified()
    sac.transition_to_auditee_certified()
    sac.transition_to_submitted()
    sac.transition_to_disseminated()
    sac.save()


def disseminate(sac, year):
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
        return in_wb.strip() == in_json.strip()
    elif in_wb is None or in_json is None:
        return are_they_both_none_or_empty(in_wb, in_json)
    else:
        return in_wb == in_json


def get_api_values(endpoint, rid, field):
    api_url = settings.POSTGREST.get(settings.ENVIRONMENT)
    res = call_api(api_url, endpoint, rid, field)

    if res.status_code == 200:
        # print(f'{res.status_code} {res.url} {res.json()}')
        return list(map(lambda d: d[field], res.json()))
    else:
        print(f"{res.status_code} {res.url}")
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
        print(f"-------------------- {endpoint} --------------------")
        summary = {}
        for row_ndx, row in enumerate(endo["rows"]):
            count(summary, "total_rows")
            equality_results = []
            for field_ndx, f in enumerate(row["fields"]):
                # logger.info(f"Checking /{endpoint} {report_id} {f}")
                # logger.info(f"{get_api_values(endpoint, report_id, f)}")
                api_values = get_api_values(endpoint, report_id, f)
                this_api_value = api_values[row_ndx]
                this_field_value = row["values"][field_ndx]
                eq = check_equality(this_field_value, this_api_value)
                if not eq:
                    logger.info(
                        f"Does not match. [eq {eq}] [field {f}] [field val {this_field_value}] != [api val {this_api_value}]"
                    )
                equality_results.append(eq)

            if all(equality_results):
                count(summary, "correct_fields")
            else:
                count(summary, "incorrect_fields")
                sys.exit(-1)
        logger.info(summary)
        combined_summary = combine_counts(combined_summary, summary)
    return combined_summary


def generate_workbooks(user, dbkey, year, result):
    try:
        entity_id = "DBKEY {dbkey} {year} {date:%Y_%m_%d_%H_%M_%S}".format(
            dbkey=dbkey, year=year, date=datetime.now()
        )
        sac = setup_sac(user, entity_id, dbkey)

        if sac.general_information["audit_type"] == "alternative-compliance-engagement":
            print(f"Skipping ACE audit: {dbkey}")
            raise DataMigrationError("Skipping ACE audit")
        else:
            builder_loader = workbook_builder_loader(user, sac, dbkey, year)
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

            disseminate(sac, year)
            combined_summary = api_check(json_test_tables)
            logger.info(combined_summary)

            result["success"].append(f"{sac.report_id} created")
    except Exception as exc:
        tb = traceback.extract_tb(sys.exc_info()[2])
        for frame in tb:
            print(f"{frame.filename}:{frame.lineno} {frame.name}: {frame.line}")

        result["errors"].append(f"{exc}")


def run_end_to_end(email, dbkey, year, result):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.info("No user found for %s, have you logged in once?", email)
        return

    generate_workbooks(user, dbkey, year, result)
