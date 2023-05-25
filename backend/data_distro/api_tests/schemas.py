import json
import _jsonnet
import jsonschema

PATH = "/src/data_distro/api_tests/schema"

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

def _view_to_sonnet(api_view):
    view_name = api_view.replace('vw_', '')
    return f"{PATH}/{view_name}.jsonnet"
    
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
        try:
            json_str = _jsonnet.evaluate_file(_view_to_sonnet(api_view))
        except Exception as e:
            raise e
        schema_cache[api_view] = json.loads(json_str)    
    schema = schema_cache[api_view]
    return schema

def validate_api_object(api_view, api_object):
    validation_error = None
    # This is not what we should do.
    obj = {}
    if api_view in _transforms:
        for k, v in api_object.items():    
            if k in _transforms[api_view]:
                obj[k] = _transforms[api_view][k](v)
            else:
                obj[k] = v
    else:
        obj = api_object
    
    validator = jsonschema.Draft7Validator(get_schema(api_view))
    errors = validator.iter_errors(obj)
    return errors
