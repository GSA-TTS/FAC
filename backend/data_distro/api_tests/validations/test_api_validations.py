import json
from jsonschema import validate
from fac import FAC


def test_auditee_0():
    schema = json.load(open("schema/auditee.json"))
    auditee_0 = json.load(open("inputs/auditee_0.json"))
    assert validate(instance=auditee_0, schema=schema) == None

def test_auditees():
    schema = json.load(open("schema/auditee.json"))
    for i in range(1, 10):
        result_set = FAC().table('vw_auditee').limits(0, 1000, 500).run()
        print("result_set length:", len(result_set))
        failure_count = 0
        for auditee in result_set:
            try:
                validate(instance=auditee, schema=schema)
            except:
                failure_count += 1
        print("auditee assertion failures", failure_count)
        assert failure_count == 0
            