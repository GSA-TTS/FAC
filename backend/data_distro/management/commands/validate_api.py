
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


class Command(BaseCommand):
    help = """
        Runs validations on the API endpoints.

        Becase the API presents *views* of the data, these tests run JSON Schema validations
        over the data when round-tripped from the Census import through to the PostgREST 
        API export.
    """

    def add_arguments(self, parser):
        parser.add_argument("--view", type=str, help="API view", default="vw_general")
        parser.add_argument(
            "-y",
            "--year",
            type=int,
            help="Four digit year to be validated",
            default=2022
            )
        parser.add_argument("--start", type=int, help="Result set start location", default=0)
        parser.add_argument("--end", type=int, help="Result end location", default=100)
        parser.add_argument("--step", type=int, help="Result set step size")

    def handle(self, *args, **kwargs):
        print(kwargs)
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
