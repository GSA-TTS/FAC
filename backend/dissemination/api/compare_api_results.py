# flake8: noqa
import argparse
import csv


from lib.api_support import (
    compare,
)

import sys
import json

# How to run the script manually
# Running against a report id
# python compare_api_results.py --environment local --scheme http --api_base_1 localhost --api_version_1 api_v1_1_0 --api_base_2 localhost --api_version_2 api_v1_1_0 --endpoint general --port 3000 --report_id 2023-06-GSAFAC-0000000733
# Running against a date range
# python compare_api_results.py --environment local --scheme http --api_base_1 localhost --api_version_1 api_v1_1_0 --api_base_2 localhost --api_version_2 api_v1_1_0 --endpoint general --port 3000 --start_date 2023-03-01 --end_date 2023-03-02


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", type=str)

    parser.add_argument("--scheme", type=str)
    parser.add_argument("--port", type=int, default=443)

    parser.add_argument("--api_base_1", type=str)
    parser.add_argument("--api_base_2", type=str)

    parser.add_argument("--api_version_1", type=str)
    parser.add_argument("--api_version_2", type=str)

    parser.add_argument("--endpoint", type=str)
    parser.add_argument("--report_id", type=str)

    parser.add_argument("--start_date", type=str)
    parser.add_argument("--end_date", type=str)
    parser.add_argument("--audit_year", type=str)
    parser.add_argument(
        "--output_csv",
        type=str,
        help="Path to save mismatch details (CSV)",
        default="STDOUT",
    )
    # parser.add_argument("--strict_order", type=bool, default=True)
    parser.add_argument("--strict_order", dest="strict_order", action="store_true")
    parser.add_argument("--any_order", dest="strict_order", action="store_false")

    parser.add_argument("--comparison_key", type=str, default="report_id")

    parser.add_argument("--ignore", type=str, default=None)
    return parser


def null_string(v):
    if v is None:
        return "<null>"
    else:
        return v


allow_multiple = ["missing_in_l1", "missing_in_l2", "mappings_not_equal", "dict_values"]


def output_results(args, result):
    if isinstance(result, list):
        # for r in result:
        #     print(r)
        # return False
        # Collect all error pairs
        all_errors = []
        used_keys = set()

        result_list = result if isinstance(result, list) else [result]
        for r in result_list:
            for error in r.get_errors():
                # was error.e1.key and error.e2.key...
                if error.type in used_keys:
                    pass
                else:
                    if error.type not in allow_multiple:
                        # print(error.type)
                        used_keys.add(error.type)
                    all_errors.append(
                        {
                            "error_type": error.type,
                            "api_version_1": error.e1.version,
                            "key_1": error.e1.key,
                            "value_1": null_string(error.e1.value),
                            "report_id_1": error.e1.report_id,
                            "api_version_2": error.e2.version,
                            "key_2": error.e2.key,
                            "value_2": null_string(error.e2.value),
                            "report_id_2": error.e2.report_id,
                        }
                    )

        if args.output_csv == "STDOUT":
            handle = sys.stdout
        else:
            handle = open(args.output_csv, "w", newline="", encoding="utf-8")

        # Write CSV if needed
        if args.output_csv:

            separator = ","
            quote = '"'
            with handle as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "error_type",
                        "api_version_1",
                        "key_1",
                        "value_1",
                        "report_id_1",
                        "api_version_2",
                        "key_2",
                        "value_2",
                        "report_id_2",
                    ],
                    delimiter=separator,
                    quotechar=quote,
                    quoting=csv.QUOTE_NONNUMERIC,
                )
                writer.writeheader()
                writer.writerows(all_errors)
            # print(f"Mismatch results saved to {args.output_csv}")

            if handle is not sys.stdout:
                handle.close()


def main():
    # Set up and run the argument parser
    parser = setup_parser()
    args = parser.parse_args()

    # Everything that follows is argument validation.
    # All of the work is done by `compare`.
    # This lets us write tests against everything in the command.

    if args.scheme is None:
        print("`scheme` must be http or https")
        sys.exit(-1)

    # Check that we have base URLs for the two APIs.
    for api_base in ["api_base_1", "api_base_2"]:
        if getattr(args, api_base) is None:
            print(
                f"You must provide an initial API base URL for comparison (missing {api_base})"
            )
            sys.exit(-1)

    # Check that we have api versions.
    for api_version in ["api_version_1", "api_version_2"]:
        if getattr(args, api_version) is None:
            print(f"You must provide an API version (missing {api_version}). Exiting.")
            sys.exit(-1)

    # Make sure we have a table
    if args.endpoint is None:
        print("You must provide an endpoint (e.g. `general`). Exiting.")
        sys.exit(-1)

    # We must have a report_id, a start/end date, or an audit year.
    if (
        (not args.report_id)
        and (not args.start_date and not args.end_date)
        and (not args.audit_year)
    ):
        print(
            "You must provide either a report_id, a start/end date range, or an audit year. Exiting."
        )
        sys.exit(-1)

    if args.start_date or args.end_date:
        if args.start_date and not args.end_date:
            print("You provided a start date with no end date. Exiting.")
            sys.exit(-1)

        if not args.start_date and args.end_date:
            print("You provided an end date without a start date. Exiting.")
            sys.exit(-1)

        if args.audit_year:
            print(
                "You provided a start/end date with an audit year. Choose one. Exiting."
            )
            sys.exit(-1)

    if not args.environment and args.environment not in ["local", "cloud"]:
        print("--environment must be either `local` or `cloud`")
        sys.exit(-1)

    # The ignore file is a JSON dictionary
    ignore = {}
    if args.ignore is not None:
        ignore = json.load(open(args.ignore))

    result = compare(
        scheme=args.scheme,
        api_base_1=args.api_base_1,
        api_base_2=args.api_base_2,
        api_version_1=args.api_version_1,
        api_version_2=args.api_version_2,
        endpoint=args.endpoint,
        port=args.port,
        report_id=args.report_id,
        start_date=args.start_date,
        end_date=args.end_date,
        audit_year=args.audit_year,
        environment=args.environment,
        comparison_key=args.comparison_key,
        strict_order=args.strict_order,
        ignore=ignore,
    )

    output_results(args, result)


if __name__ in "__main__":
    main()
