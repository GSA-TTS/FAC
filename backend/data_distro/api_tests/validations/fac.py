import os
import requests
import typing
from typing import List, Set, Dict, Tuple

URI="https://api.data.gov/TEST/audit-clearinghouse/v0/dissemination"
if os.getenv("API_GOV_URL") is not None:
    URI = os.getenv("API_GOV_URL")

class FAC:
    def __init__(self, 
                 api_key=os.getenv("API_GOV_KEY"),
                 api_uri=URI,
                 ):
        self.api_key = api_key
        self.api_uri = api_uri
        self._select = None
        self._table = None
        self._queries = list()
        self._start = 0
        self._end = 10
        self._step = 1000
        self._url = ""
        self._headers = {"X-API-Key": api_key}
        self._debug = False
    
    def select(self, list_of_columns : List[str]):
        self._select = list_of_columns
        return self
    
    def table(self, table : str):
        self._table = table
        return self

    def query(self, op, column, value):
        if op in ["eq", "gt", "lt"]:
            q = f"{column}={op}.{value}"
        self._queries.append(q)
        return self

    def limits(self, start=0, end=1000, step=1000):
        self._start = start
        self._end = end
        self._step = step
        self._headers["Range"] = f"{start}-{end}"
        return self

    def debug(self):
        self._debug = True
        return self

    def compose(self):
        url = ""
        if self._table is not None:
            url += f"/{self._table}"
        else:
            raise Exception("No table provided for FAC query.")

        # Make sure not to assign a reference to the _queries list...
        query_params = list() + self._queries
        if self._select is not None:
            query_params.append(f"select={','.join(self._select)}")
        
        url += "?" + "&".join(query_params)
        self._url = url
        return self

    def get_results(self):
        qurl = self.api_uri + self._url
        if self._debug:
            print(qurl)
        # print(f'[ {qurl} ]')
        results = []
        for start_point in range(self._start, self._end, self._step):
            step_end = start_point + self._step
            if step_end > self._end:
                step_end = self._end - 1
            if self._debug:
                print(f'\t-- start[{start_point}] end[{step_end}] query_url[{qurl}]')
            res = requests.get(qurl, headers={'Range-Unit': "items", 
                                            "Range": f'{start_point}-{step_end}',
                                            'X-Api-Key': self.api_key
                                            })
            json = res.json()
            if len(json) == 0:
                break
            # FIXME: There could be a list of length four when we have
            # an error... look more closely.
            if 'code' in json:
                print(f"code: {json['code']}, msg: {json['message']}")
                break
            else:
                if self._debug:
                    print(f'\t\tlen({len(json)})')
                results += json
        return results

    def path(self):
        self.compose()
        return self._url
    def url(self):
        self.compose()
        return self.api_uri + self._url
    def headers(self):
        return self._headers
    
    def run(self):
        self.compose()
        res = self.get_results()
        return res

if __name__ == "__main__":
    fac = FAC()
    fac.table("vw_general").select(["id", "audit_year"]).limits(0, 1000, 1000).query("lt", "id", "50")
    print(fac.path())
    print(fac.url())
    res = fac.run()
    print(res)