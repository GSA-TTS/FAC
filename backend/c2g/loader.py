import datetime


from audit.models import SingleAuditChecklist
from .models import ELECAUDITHEADER as Gen
from .wb_generator import load_historic_data


def load_data():
    SingleAuditChecklist.objects.all().delete
    result_log = {}
    gens = Gen.objects.filter(AUDITYEAR="2022")
    total_count = error_count = 0
    for gen in gens:
        audit_year = gen.AUDITYEAR
        dbkey = gen.DBKEY
        result = load_historic_data(audit_year, dbkey)
        result_log[(audit_year, dbkey)] = result
        total_count += 1
        if len(result["errors"]) > 0:
            error_count += 1
            print(result)
        if error_count > 25:
            break

        if total_count % 25 == 0:
            now = datetime.datetime.now()
            print(now.strftime("%H:%M"))
            print(f"{error_count} errors out of {total_count}")

    print("********* Loader Summary ***************")
    print(f"{error_count} errors out of {total_count}")
    for k, v in result_log.items():
        print(k, v)
        print("-------------------")
