import json
from jsonschema import validate
from fac import FAC
from time import time
from multiprocessing import Pool


def test_auditee_0():
    schema = json.load(open("schema/auditee.json"))
    auditee_0 = json.load(open("inputs/auditee_0.json"))
    assert validate(instance=auditee_0, schema=schema) == None


def validations(view_name, result_set, schema):
    failure_count = 0
    start = time()
    for obj in result_set:
        try:
            validate(instance=obj, schema=schema)
        except:
            failure_count += 1
    if len(result_set) > 0:
        print(f"loop time: {time() - start} each: {(time() - start)/len(result_set)}")
    print(f"{view_name} assertion failures: {failure_count}")
    return failure_count

def _test_framing(view_name, schema_file):
    schema = json.load(open(schema_file))
    failure_count = 0
    loop_step = 10000
    for id_range in map(lambda ndx: (ndx*loop_step, (ndx*loop_step)+loop_step), range(0, 10)):
        print(id_range)
        start = time()
        result_set = (FAC()
                      .table(view_name)
                      .limits(id_range[0], id_range[1], loop_step//2)
                      .debug()
                      ).run()
        print(f"query time: {(time() - start)}")
        print("result_set length:", len(result_set))
        failure_count += validations(view_name, result_set, schema)
    return failure_count


def test_general():
    failure_count = _test_framing("vw_general", "schema/general.json")
    assert failure_count == 0

def test_auditees():
    failure_count = _test_framing("vw_auditee", "schema/auditee.json")
    assert failure_count == 0
