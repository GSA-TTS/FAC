import datetime


from audit.models import SingleAuditChecklist
from .models import ELECAUDITHEADER as Gen
from .wb_generator import load_historic_data

# we'll deal with these submissions later as they have data issues
EXCLUSION_LIST = [
    # ("2022", "183126"),
    # ("2022", "45486"),
]
PRIORITY_LIST = [
    # ("2022", "194017"),
]


def load_data():
    SingleAuditChecklist.objects.all().delete()
    result_log = {}
    gens = Gen.objects.filter(AUDITYEAR="2022")
    total_count = error_count = 0
    for audit_year, dbkey in PRIORITY_LIST:
        result = load_historic_data(audit_year, dbkey)
        result_log[(audit_year, dbkey)] = result
        total_count += 1
        if len(result["errors"]) > 10:
            error_count += 1

    for gen in gens:
        audit_year = gen.AUDITYEAR
        dbkey = gen.DBKEY
        if (audit_year, dbkey) in EXCLUSION_LIST:
            continue
        result = load_historic_data(audit_year, dbkey)
        result_log[(audit_year, dbkey)] = result
        total_count += 1
        if len(result["errors"]) > 0:
            error_count += 1
            print(result)
        if error_count > 0:
            break

    print("********* Loader Summary ***************")
    print(f"{error_count} errors out of {total_count}")
    for k, v in result_log.items():
        print(k, v)
        print("-------------------")
