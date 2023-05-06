
"""
Download data from https://facdissem.census.gov/PublicDataDownloads.aspx
Then unzip the files and place the them in data_distro/data_to_load/

Load them with: manage.py public_data_loader
"""
from django.core.management.base import BaseCommand

from data_distro.api_tests import (
    fac,
    schemas
)
from data_distro.management.commands.handle_errors import (
    set_up_error_files,
    log_results,
)


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
    for id_range in map(lambda ndx: (ndx * loop_step, (ndx * loop_step) + loop_step), range(0, 10)):
        print(id_range)
        start = time()
        result_set = (FAC()
                      .table(view_name)
                      .limits(id_range[0], id_range[1], loop_step // 2)
                      .debug()
                      ).run()
        print(f"query time: {(time() - start)}")
        print("result_set length:", len(result_set))
        failure_count += validations(view_name, result_set, schema)
    return failure_count


class Command(BaseCommand):
    help = """
        Runs validations on the API endpoints.

        Becase the API presents *views* of the data, these tests run JSON Schema validations
        over the data when round-tripped from the Census import through to the PostgREST 
        API export.
    """

    def add_arguments(self, parser):
        parser.add_argument("--view", type=str, help="API view")
        parser.add_argument(
            "-y",
            "--year",
            type=int,
            help="Four digit year to be validated",
        )
        parser.add_argument("--start", type=int, help="Result set start location")
        parser.add_argument("--end", type=int, help="Result end location")
        parser.add_argument("--step", type=int, help="Result set step size")

    def handle(self, *args, **kwargs):
        print(kwargs)
        if kwargs["year"] == None:
            kwargs["year"] = 2022
        if kwargs["view"] == None:
            kwargs["view"] = "vw_general"
        if kwargs["start"] == None:
            kwargs["start"] = 0
        if kwargs["end"] == None:
            kwargs["end"] = 10000
        if kwargs["step"] == None:
            kwargs["step"] = (kwargs["end"] - kwargs["start"]) // 2
         
        failure_count = 0
        validation_errors = []
        result_set = (fac.FAC()
                        .table(kwargs["view"])
                        .limits(kwargs["start"], kwargs["end"], kwargs["step"])
                        .query("eq", "audit_year", kwargs["year"])
                        .debug()
                        ).run()
        if len(result_set) == 0:
            print(f"No results: {result_set}")
        for obj in result_set:
            validation_result = schemas.validate_api_object(kwargs["view"], obj)
            if validation_result is not None:
                validation_errors.append({"object": obj, "error": validation_result})
                failure_count += 1

        for oe in validation_errors:
            print(f"OBJECT\n------")
            print(oe["object"])
            print(f"\nERROR\n-----")
            print(oe["error"])
            print()
        return f"failure_count: {failure_count}"
