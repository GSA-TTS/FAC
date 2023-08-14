from django.apps import apps
from django.core.management.base import BaseCommand
from users.models import User

import argparse
import datetime
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
parser = argparse.ArgumentParser()

# Peewee runs a really noisy DEBUG log.
pw = logging.getLogger('peewee')
pw.addHandler(logging.StreamHandler())
pw.setLevel(logging.INFO)

from audit.fixtures.workbooks.workbook_creation import (
    sections,
    workbook_loader,
    setup_sac,
)


from audit.fixtures.workbooks.sac_creation import _post_upload_pdf

# # def transition(sac):
# #     SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
# #     # I couldn't use the transition functions. Don't know why.
# #     # In progress
# #     sac.transition_name.append(SingleAuditChecklist.STATUS.SUBMITTED)
# #     sac.transition_date.append(datetime.date.today())

# #     sac.transition_name.append(SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED)
# #     sac.transition_date.append(datetime.date.today())

# #     sac.transition_name.append(SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED)
# #     sac.transition_date.append(datetime.date.today())

# #     sac.transition_name.append(SingleAuditChecklist.STATUS.CERTIFIED)
# #     sac.transition_date.append(datetime.date.today())

# # def cross_validate(sac):
# #     print("CROSS VALIDATING")
# #     validation_functions = audit.cross_validation.functions

# #     shape = audit.cross_validation.sac_validation_shape(sac)
# #     for fun in validation_functions:
# #         fun(shape)

# #     sac.validate_cross()

# # def etl(sac):
# #     print("TRANSFERRING DATA... HARDER BETTER FASTER STRONGER ...")
# #     from audit.etl import ETL

# #     if sac.general_information:
# #         etl = ETL(sac)
# #         etl.load_all()

#     sac.transition_name.append(SingleAuditChecklist.STATUS.SUBMITTED)
#     sac.transition_date.append(date.today())

def step_through_certifications(sac, SAC):
    sac.transition_name.append(SAC.STATUS.SUBMITTED)
    sac.transition_date.append(datetime.date.today())

    sac.transition_name.append(SAC.STATUS.AUDITOR_CERTIFIED)
    sac.transition_date.append(datetime.date.today())

    sac.transition_name.append(SAC.STATUS.AUDITEE_CERTIFIED)
    sac.transition_date.append(datetime.date.today())

    sac.transition_name.append(SAC.STATUS.CERTIFIED)
    sac.transition_date.append(datetime.date.today())

from dissemination.models import (
    FindingText,
    Finding,
    FederalAward,
    CapText,
    Note,
    Revision,
    Passthrough,
    General,
    SecondaryAuditor,
)

from audit.etl import ETL
    
def disseminate(sac):
    print("TRANSFERRING DATA... HARDER BETTER FASTER STRONGER ...")
    for model in [FindingText,
            Finding,
            FederalAward,
            CapText,
            Note,
            Revision,
            Passthrough,
            General,
            SecondaryAuditor
        ]:
        model.objects.filter(report_id=sac.report_id).delete()

    if sac.general_information:
        etl = ETL(sac)
        etl.load_all()

# [{'endpoint': 'federal_awards',
#   'report_id': '2022TEST000100010',
#   'rows': [{'fields': ['program_name',
#                        'federal_program_total',
#                        'cluster_total',
#                        'is_guaranteed',
#                        'is_direct',
#                        'is_passed',
#                        'subrecipient_amount',
#                        'is_major',
#                        'amount_expended',
#                        'federal_program_total',
#                        'passthrough_name',
#                        'passthrough_identifying_number'],
#             'values': ['COMMUNITY FACILITIES LOANS AND GRANTS',
#                        '69038',
#                        '0',
#                        'N',
#                        'Y',
#                        'N',
#                        '0',
#                        'N',
#                        '69038',
#                        '69038',
#                        '',
#                        '']},

from pprint import pprint
from config import settings

import os


import jwt
import requests

def create_payload(api_url, role="api_fac_gov"):
    payload = {
        # PostgREST only cares about the role.
        "role": role,
        "created": datetime.datetime.today().isoformat(),
    }
    return payload

def call_api(api_url, endpoint, rid, field):
    # We must pass a properly signed JWT to access the API
    encoded_jwt = jwt.encode(
        create_payload(api_url), os.getenv("PGRST_JWT_SECRET"), algorithm="HS256"
    )
    full_request = f'{api_url}/{endpoint}?report_id=eq.{rid}&select={field}'
    response = requests.get(
        full_request, headers={"Authorization": f"Bearer {encoded_jwt}"}, timeout=10
    )
    return response

import re
import math
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
        return True if math.isclose(float(in_wb), float(in_json),rel_tol=1e-1) else False 
    elif isinstance(in_wb, str) and isinstance(in_json, str):
        return in_wb.strip() == in_json.strip()
    elif in_wb is None or in_json is None:
        return are_they_both_none_or_empty(in_wb, in_json)
    else:
        return in_wb == in_json

def get_api_values(endpoint, rid, field):
    api_url = settings.POSTGREST.get("URL")
    res = call_api(api_url, endpoint, rid, field)
    
    if res.status_code == 200:
        # print(f'{res.status_code} {res.url} {res.json()}')
        return list(map(lambda d: d[field], res.json()))
    else:
        print(f'{res.status_code} {res.url}')
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
    combined_summary = {'endpoints': 0, 'correct_rows': 0, 'incorrect_rows': 0}
    for endo in json_test_tables:
        count(combined_summary, 'endpoints')
        endpoint = endo['endpoint']
        report_id = endo['report_id']
        print(f"-------------------- {endpoint} --------------------")
        summary = {}
        for row_ndx, row in enumerate(endo['rows']):
            count(summary, 'total_rows')
            equality_results = []
            for field_ndx, f in enumerate(row['fields']):
                api_values = get_api_values(endpoint, report_id, f)
                # print(api_values)
                this_api_value = api_values[row_ndx]
                this_field_value = row['values'][field_ndx]
                eq = check_equality(this_field_value, this_api_value)
                if not eq:
                    print(f'eq {eq} field {f} fval {this_field_value} == aval {this_api_value}')
                equality_results.append(eq)
                    
            if all(equality_results):
                print(f"------ YESYESYES")
                count(summary, 'correct_rows')
            else:
                print(f"------ NONONO")
                count(summary, 'incorrect_rows')
                print(equality_results)
                sys.exit()
                # print(row)
        print(summary)
        combined_summary = combine_counts(combined_summary, summary)
    return combined_summary

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, required=True)
        parser.add_argument("--dbkey", type=str, required=True)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(email=options["email"])
        except User.DoesNotExist:
            logger.info(
                "No user found for %s, have you logged in once?", options["email"]
            )
            return
        entity_id = "DBKEY {dbkey} {date:%Y_%m_%d_%H_%M_%S}".format(
            dbkey=options["dbkey"], date=datetime.datetime.now()
        )
        sac = setup_sac(user, entity_id, options["dbkey"])
        loader = workbook_loader(user, sac, options["dbkey"], entity_id)
        json_test_tables = []
        for section, fun in sections.items():
            # FIXME: Can we conditionally upload the addl' and secondary workbooks?
            (_, json, _) = loader(fun, section)
            json_test_tables.append(json)
        _post_upload_pdf(sac, user, 'audit/fixtures/basic.pdf')
        SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
        step_through_certifications(sac, SingleAuditChecklist)
        disseminate(sac)
        # pprint(json_test_tables)
        combined_summary = api_check(json_test_tables)
        print(combined_summary)
