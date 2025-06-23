from collections import namedtuple as NT
from requests import get
from requests import Request
from typing import Union
from time import time
from datetime import timedelta
from math import floor

FAC_PRODUCTION = "https://api.fac.gov"

Param = NT("Param", "key,value")
Query = NT("Query", "key,op,value")
Header = NT("Header", "key,value")


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class FAC:

    def __init__(
        self, scheme="https", port=443, base=FAC_PRODUCTION, endpoint="general"
    ):
        self._scheme = scheme
        self._port = port
        self._base = base
        self._endpoint = endpoint
        self._params = []
        self._metadata = dict()
        self.error = None
        self._results = list()
        self._structs = list()
        # Default headers
        # FIXME: We should just be publishing the API we want to be using
        # by default. This needs to go away eventually.
        self._headers = dict()
        self._headers["Accept-Profile"] = "api_v1_1_0"

    def scheme(self, scheme):
        self._scheme = scheme
        return self

    def port(self, port):
        self._port = port
        return self

    def base(self, base):
        self._base = base
        return self

    def endpoint(self, ep):
        self._endpoint = ep
        return self

    def param(self, key, value, noisy=True):
        if key in ["limit", "offset"] and noisy:
            print(
                "WARNING: `limit` and `offset` will be overridden; use headers instead."
            )
            print(
                "See https://docs.postgrest.org/en/v12/references/api/pagination_count.html#limits-and-pagination"
            )
        # Limit and offset can only occur once.
        # If we're about to use one, remove it from the list and
        # use the new value.
        if key in ["limit", "offset"]:
            self._params = list(
                filter(
                    lambda obj: (
                        None if isinstance(obj, Param) and obj.key == key else obj
                    ),
                    self._params,
                )
            )

        self._params.append(Param(key, value))
        return self

    def query(self, key, op, value):
        self._params.append(Query(key, op, value))
        return self

    def header(self, key, value):
        self._headers[key] = value
        return self

    def headers(self, headers):
        self._headers = headers
        return self

    def _params_to_list(self):
        ls = []
        for obj in self._params:
            if isinstance(obj, Param):
                ls.append((obj.key, obj.value))
            elif isinstance(obj, Query):
                ls.append((obj.key, f"{obj.op}.{obj.value}"))
            else:
                self.error = {
                    "code": "UNKNOWN PARAM OBJECT",
                    "message": "Unknown object: {obj}",
                }
        return ls

    def get_url(self):
        p = Request(
            "GET",
            f"{self._scheme}://{self._base}:{self._port}/{self._endpoint}",
            params=self._params_to_list(),
            headers=self._headers,
        ).prepare()
        return p.url

    def api_key(self, key):
        self.header("x-api-key", key)

    def fetch(self):
        fetching = True
        results = []
        self._results = []
        offset = 0
        inc = 20000
        while fetching:
            self.param("offset", offset, noisy=False)
            self.param("limit", ((offset + inc) - 1), noisy=False)
            t0 = time()
            URL = f"{self._scheme}://{self._base}:{self._port}/{self._endpoint}"
            res = get(
                URL,
                params=self._params_to_list(),
                headers=self._headers,
            )

            t1 = time()
            if "elapsed_time" in self._metadata:
                self._metadata["elapsed_time"].append(t1 - t0)
            else:
                self._metadata["elapsed_time"] = [t1 - t0]
            if "query_count" in self._metadata:
                self._metadata["query_count"] += 1
            else:
                self._metadata["query_count"] = 1

            try:
                resj = res.json()
            except:
                resj = None
            # Look to see if things died.
            if not resj:
                fetching = False
                self.error = {
                    "code": "NON_JSON_RESPONSE",
                    "message": "Received no JSON in the response.",
                }
                return self
            elif len(resj) == 0:
                fetching = False
                self.error = {
                    "code": "ZERO_LENGTH_RESPONSE",
                    "message": "No values in the JSON response.",
                }
                return self
            elif "error" in resj:
                fetching = False
                self.error = resj["error"]
                return self
            # Don't do an extra query if we're done.
            elif len(resj) < inc - 1:
                results += resj
                self._results += results
                self.error = None
                return self
            # Keep going.
            else:
                results += resj
                offset += inc
                # print(f"fetched {len(results)}; offset {offset}")
        # Shouldn't get here
        return self

    def error_status(self):
        return self.error

    def results(self):
        return self._results

    def structs(self):
        if len(self._structs) > 0:
            return self._structs
        else:
            self._structs = list(map(lambda s: Struct(**s), self._results))
            return self._structs

    def metadata(self):
        if "elapsed_time" in self._metadata:
            total_time = sum(self._metadata["elapsed_time"])
            average_query_time = round(total_time / self._metadata["query_count"], 3)
            self._metadata["total_time"] = round(total_time, 3)
            self._metadata["average_query_time"] = average_query_time
            self._metadata["total_time_hms"] = str(timedelta(seconds=floor(total_time)))
            keep = ["total_time", "average_query_time", "query_count", "total_time_hms"]
            new = dict()
            for k in keep:
                new[k] = self._metadata[k]
            return new
        else:
            return {}

    def append_metadata(self, other_client):
        us = self._metadata
        them = other_client._metadata
        if "elapsed_time" in them:
            us["elapsed_time"] = us["elapsed_time"] + them["elapsed_time"]
        if "query_count" in them:
            us["query_count"] += them["query_count"]
        return self
