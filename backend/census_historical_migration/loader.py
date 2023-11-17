from .models import ELECAUDITHEADER as Gen
from .make_submission import load_historic_data


def load_data(audit_year):
    result_log = {}
    total_count = error_count = 0
    gens = Gen.objects.filter(AUDITYEAR=audit_year)
    for gen in gens:
        dbkey = gen.DBKEY
        result = load_historic_data(audit_year, dbkey)

        result_log[(audit_year, dbkey)] = result
        total_count += 1
        if len(result["errors"]) > 0:
            error_count += 1
        if total_count % 5 == 0:
            print(f"Processed = {total_count}, Errors = {error_count}")
        if error_count > 5:
            break

    print("********* Loader Summary ***************")
    for k, v in result_log.items():
        print(k, v)
        print("-------------------")
    print(f"{error_count} errors out of {total_count}")
