# flake8: noqa
from requests import get
import lib.fac as f

from lib.compare_json_objects import (
    compare_lists_of_json_objects as clojo,
    compare_sefa,
    Result,
)

import os
import sys


def get_api_key(env_var: str):
    return os.getenv(env_var)


def build_headers_base(environment: str):
    header_keys = {}

    if environment == "local":
        for local_var in ["FAC_API_JWT", "FAC_API_USER_ID"]:
            if not os.getenv(local_var):
                print(f"env var {local_var} not set locally")
                return None
        header_keys["authorization"] = "bearer " + os.getenv("FAC_API_JWT", "NOJWT")
        header_keys["x-api-user-id"] = os.getenv("FAC_API_USER_ID", "NOUSERID")

    elif environment == "cloud":
        for cloud_var in ["FAC_API_KEY"]:
            if not os.getenv(cloud_var):
                print(f"env var {cloud_var} not set in cloud")
                return None
        header_keys["x-api-key"] = os.getenv("FAC_API_KEY", "NOAPIKEY")
    else:
        # Return as an error if we did not set the environment correctly.
        return None

    return header_keys


def append_headers(base, to_append):
    new = {}
    for k, v in base.items():
        new[k] = v

    for k, v in to_append.items():
        new[k] = v

    return new


def build_query_url(
    scheme, base, port, endpoint, report_id=None, start_date=None, end_date=None
):
    url = f"{scheme}://{base}:{port}/{endpoint}"

    if report_id:
        url += f"?report_id=eq.{report_id}"
    elif start_date and end_date:
        url += f"?fac_accepted_date=gte.{start_date}&fac_accepted_date=lt.{end_date}"

    return url


def compare(
    scheme,
    api_base_1,
    api_base_2,
    api_version_1,
    api_version_2,
    endpoint,
    port,
    report_id=None,
    start_date=None,
    end_date=None,
    audit_year=None,
    environment="local",
    comparison_key="report_id",
    strict_order=True,
    ignore={},
):

    # The base headers are different in the local environment and in the cloud.
    # when testing locally, we need a user ID and at JWT
    # when testing against the cloud, we need an API key
    headers_base = build_headers_base(environment)
    if not headers_base:
        print("could not build HTTP headers. exiting.")
        sys.exit(-1)

    # Now, we build a query URL. We're building different URLs depending on whether
    # we're testing one single report, a date range, or an audit year.
    if report_id:
        client_1 = f.FAC()
        client_1.scheme(scheme).port(port).base(api_base_1).endpoint(endpoint)
        client_1.query("report_id", "eq", report_id)
        client_2 = f.FAC()
        client_2.scheme(scheme).port(port).base(api_base_2).endpoint(endpoint)
        client_2.query("report_id", "eq", report_id)
    elif start_date and end_date:
        client_1 = f.FAC()
        client_1.scheme(scheme).port(port).base(api_base_1).endpoint(endpoint)
        client_1.query("fac_accepted_date", "gte", start_date)
        client_1.query("fac_accepted_date", "lt", end_date)
        client_2 = f.FAC()
        client_2.scheme(scheme).port(port).base(api_base_2).endpoint(endpoint)
        client_2.query("fac_accepted_date", "gte", start_date)
        client_2.query("fac_accepted_date", "lt", end_date)
    elif audit_year:
        client_1 = f.FAC()
        client_1.scheme(scheme).port(port).base(api_base_1).endpoint(endpoint)
        client_1.query("audit_year", "eq", audit_year)
        client_2 = f.FAC()
        client_2.scheme(scheme).port(port).base(api_base_2).endpoint(endpoint)
        client_2.query("audit_year", "eq", audit_year)

    # Build the distinct headers for each API by adding unique values
    # to the common base. We explicitly want the same headers *except for the API version*.
    # This lets us test (e.g.) API version 1.1.0 against 1.2.0.
    headers_1 = append_headers(headers_base, {"accept-profile": api_version_1})
    headers_2 = append_headers(headers_base, {"accept-profile": api_version_2})

    client_1.headers(headers_1)
    client_2.headers(headers_2)

    # print(client_1._params)
    # print(client_1.get_url())

    # Retrieve the lists of objects from the API server for the first version.
    client_1.fetch()
    if client_1.error_status() is not None:
        print("exception while calling API. exiting.")
        print("url_1:", client_1.get_url())
        print(client_1.error)
        sys.exit(-1)
    else:
        list_of_objects1 = client_1.results()

    print("client_1")
    for k, v in client_1.metadata().items():
        print(f"\t{k}: {v}")

    # Retrieve the objects from the second API.
    client_2.fetch()
    if client_2.error_status() is not None:
        print("exception while calling API. exiting.")
        print("url_2:", client_2.get_url())
        print(client_2.error)
        sys.exit(-1)
    else:
        list_of_objects2 = client_2.results()

    print("client_2")
    for k, v in client_2.metadata().items():
        print(f"\t{k}: {v}")

    # We should get only 200s.
    # for ndx, loo in enumerate([list_of_objects1, list_of_objects2]):
    #     if loo.status_code != 200:
    #         print(f"did not get status 200 for url {ndx}. exiting.")
    #         print(f"url: {[client_1.get_url(), client_2.get_url()][ndx]}")
    #         print(f"{loo.status_code}: {loo.reason}")
    #         print(f"headers: {[headers_1, headers_2][ndx]}")
    #         sys.exit(-1)

    # pprint(list_of_objects1.json())
    # print("=====================")
    # pprint(list_of_objects2.json())

    # Compare the lists of objects
    # We get a comparison key passed in; it defaults to `report_id`.
    # This means we look in the list and find matching objects based on that key.
    # The order is strict, meaning we expect API version 1 to return objects in exactly
    # the same order as objects in version 2. We can change that, which will allow for order
    # to vary... but, we have a number of data endpoints that *require* the correct sort order.

    # Either returns:
    #  - A single Result object, or
    #  - A list of Result objects
    if endpoint == "notes_to_sefa":
        result = compare_sefa(
            api_version_1,
            list_of_objects1,
            api_version_2,
            list_of_objects2,
            ignore=ignore,
        )
    else:
        result = clojo(
            api_version_1,
            list_of_objects1,  # list_of_objects1.json(),
            api_version_2,
            list_of_objects2,  # list_of_objects2.json(),
            comparison_key=comparison_key,
            strict_order=strict_order,
            ignore=ignore,
        )

    if isinstance(result, Result) and result:
        print("identical")
        return True
    else:
        print("different")
        return result
