import json
import _jsonnet
import jsonschema

PATH = "/src/data_distro/api_tests/schema"
_view_to_sonnet = {
    "vw_general": f"{PATH}/general.jsonnet",
    "vw_auditee": f"{PATH}/auditee.jsonnet"
}

sonnet_cache = {}
def get_schema(api_view):
    json_str = None
    if api_view not in sonnet_cache:
        json_str = _jsonnet.evaluate_file(_view_to_sonnet[api_view])
        sonnet_cache[api_view] = json.loads(json_str)    
    return sonnet_cache[api_view]

schema_cache = {}
def validate_api_object(api_view, api_object):
    schema = None
    if api_view not in schema_cache:
        schema_cache[api_view] = get_schema(api_view)
    schema = schema_cache[api_view]
    
    validation_error = None
    try:
        jsonschema.validate(schema=schema, instance=api_object)
    except Exception as e:
        validation_error = e
    return validation_error