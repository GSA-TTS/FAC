import json
import _jsonnet
import jsonschema

PATH = "/src/data_distro/api_tests/schema"
_view_to_sonnet = {
    "vw_general": f"{PATH}/general.jsonnet",
    "vw_auditee": f"{PATH}/auditee.jsonnet"
}

# I'd like to see this go away. This is a patch against the 
# objects as they come in to pass validation. We should instead
# improve data as it is imported.
def _zip_fix(integer):
    if len(str(integer)) == 4:
        return "0" + str(integer)
    elif len(str(integer)) == 8:
        return "0" + str(integer)
    else:
        return str(integer)

def _phone_fix(integer):
    if len(str(integer)) == 10:
        return "(" + str(integer)[0:3] + ")" + str(integer)[3:]
    else:
        return str(integer)
    
_transforms = {
    "vw_auditee": {
        "auditee_phone": lambda integer: _phone_fix(integer),
        "auditee_zip_code": lambda integer: _zip_fix(integer)
    }
}

# These caches can only grow as large as the table above.
# This saves us from reloading the files repeatedly.
schema_cache = {}

def get_schema(api_view):
    json_str = None
    if api_view not in schema_cache:
        json_str = _jsonnet.evaluate_file(_view_to_sonnet[api_view])
        schema_cache[api_view] = json.loads(json_str)    
    schema = schema_cache[api_view]
    return schema

def validate_api_object(api_view, api_object):
    validation_error = None
    try:
        # This is not what we should do.
        obj = {}
        for k, v in api_object.items():
            if k in _transforms[api_view]:
                obj[k] = _transforms[api_view][k](v)
            else:
                obj[k] = v
        jsonschema.validate(schema=get_schema(api_view), instance=obj)
    except Exception as e:
        validation_error = e
    return validation_error