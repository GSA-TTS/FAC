import datetime


from audit.models import SingleAuditChecklist
from .models import ELECAUDITHEADER as Gen


def load_data():
    SingleAuditChecklist.objects.all().delete

    gens = Gen.objects.all()
    total_count = error_count = 0
    for gen in gens:
        audit_year = gen.AUDITYEAR
        dbkey = gen.DBKEY
        result = load_historic_data(audit_year, dbkey)
        print(result)
        total_count += 1
        if len(result["errors"]) > 0:
            error_count += 1
            break
        if total_count % 25 == 0:
            now = datetime.datetime.now()
            print(now.strftime("%H:%M"))
            print(f"{error_count} errors out of {total_count}")

    print(f"{error_count} errors out of {total_count}")
