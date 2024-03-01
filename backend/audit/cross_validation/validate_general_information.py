import json
from django.conf import settings
from jsonschema import FormatChecker, validate
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError

from audit.cross_validation.naming import NC


def validate_general_information(sac_dict, *_args, **_kwargs):
    """
    Runs the general information data through JSON Schema validation.

    This largely repeats logic in
    audit.validators.validate_general_information_json,
    but that function doesn't pass along the full error context and we need that here.

    The errors this presents to the user are arcane, but should make clear that they
    must return to the General Information page, and once there they will get
    friendlier errors when they try to proceed.
    """
    all_sections = sac_dict["sf_sac_sections"]
    general_information = all_sections[NC.GENERAL_INFORMATION]
    schema_path = settings.SECTION_SCHEMA_DIR / "GeneralInformationRequired.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        validate(general_information, schema, format_checker=FormatChecker())
    except JSONSchemaValidationError as err:
        return [{"error": f"General Information: {str(err)}"}]
    return []
