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
from audit.models import SingleAuditChecklist
from random import randrange
from datetime import timedelta
import pytz


from dissemination.workbooklib.workbook_creation import (
    sections,
    workbook_loader,
    setup_sac,
)
from dissemination.workbooklib.sac_creation import _post_upload_pdf

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


# https://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)  # nosec
    return start + timedelta(seconds=random_second)


def step_through_certifications(sac):
    d1 = datetime.strptime("1/1/2017 1:30 PM", "%m/%d/%Y %I:%M %p")
    d2 = datetime.strptime("10/30/2023 4:50 AM", "%m/%d/%Y %I:%M %p")
    # https://stackoverflow.com/questions/7065164/how-to-make-a-datetime-object-aware-not-naive
    date = pytz.utc.localize(random_date(d1, d2))

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
        sac.transition_date.append(date)
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
        sac.disseminate()


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


def generate_workbooks(user, email, dbkey, year, store_files=True, run_api_checks=True):
    entity_id = "DBKEY {dbkey} {year} {date:%Y_%m_%d_%H_%M_%S}".format(
        dbkey=dbkey, year=year, date=datetime.now()
    )
    sac = setup_sac(user, entity_id, dbkey)
    if sac.general_information["audit_type"] == "alternative-compliance-engagement":
        print(f"Skipping ACE audit: {dbkey}")
    else:
        _post_upload_pdf(sac, user, "audit/fixtures/basic.pdf", store_files)

        loader = workbook_loader(user, sac, dbkey, year, entity_id, store_files)
        json_test_tables = []
        for section, fun in sections.items():
            (_, json, _) = loader(fun, section)
            json_test_tables.append(json)

        step_through_certifications(sac)
        errors = sac.validate_cross()
        pprint(errors.get("errors", "No errors found in cross validation"))

        disseminate(sac, year)
        if run_api_checks:
            combined_summary = api_check(json_test_tables)
            logger.info(combined_summary)


def run_end_to_end(email, dbkey, year, store_files=True, run_api_checks=True):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.info("Retrieve or create test data generation user.")
        test_user_email = "test-data-generator@fac.gsa.gov"
        user, created = User.objects.get_or_create(email=test_user_email)

    generate_workbooks(user, email, dbkey, year, store_files, run_api_checks)
