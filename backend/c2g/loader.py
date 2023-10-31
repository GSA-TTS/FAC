from audit.models import SingleAuditChecklist
from .models import ELECAUDITHEADER as Gen
from .wb_generator import load_historic_data


def load_data():
    SingleAuditChecklist.objects.all().delete

    gens = Gen.objects.all()
    counter = 0
    for gen in gens:
        if counter > 20:
            break
        audit_year = gen.AUDITYEAR
        dbkey = gen.DBKEY
        result = load_historic_data(audit_year, dbkey)
        print(result)
        counter += 1
