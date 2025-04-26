import os
import json
from collections import namedtuple as NT

# VCAP = NT("VCAP", "cmd rator rand")
GET = NT("GET", "key")
FIND = NT("FIND", "key value")


def get_vcap_services(vcap_commands):
    vcap = json.loads(os.getenv("VCAP_SERVICES"))
    for vc in vcap_commands:
        if isinstance(vc, GET):
            vcap = vcap[vc.key]
        elif isinstance(vc, FIND):
            # We're looking for a value in a list
            # based on the value of a key
            for o in vcap:
                if vc.key in o and o[vc.key] == vc.value:
                    vcap = o
                    break
    return vcap
