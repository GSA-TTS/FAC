from audit.utils import Util
from .base_field_maps import FormFieldInDissem, WorkbookFieldInDissem
from .sac_general_lib.report_id_generator import xform_dbkey_to_report_id
from .workbooklib.excel_creation_utils import apply_conversion_function


def generate_dissemination_test_table(
    audit_header, api_endpoint, mappings=None, objects=None
):
    """Generates a test table for verifying the API queries results."""
    table = {}
    table["endpoint"] = api_endpoint
    table["report_id"] = xform_dbkey_to_report_id(audit_header)

    if mappings and objects:
        table["rows"] = list()

        for o in objects:
            test_obj = {}
            test_obj["fields"] = []
            test_obj["values"] = []
            for m in mappings:
                # What if we only test non-null values?
                raw_value = getattr(o, m.in_db, None)
                attribute_value = apply_conversion_function(
                    raw_value, m.default, m.type
                )
                if (attribute_value is not None) and (attribute_value != ""):
                    if m.in_dissem == WorkbookFieldInDissem:
                        test_obj["fields"].append(m.in_sheet)
                        test_obj["values"].append(m.type(attribute_value))
                    else:
                        test_obj["fields"].append(m.in_dissem)
                        test_obj["values"].append(m.type(attribute_value))

            table["rows"].append(test_obj)
    else:
        table["singletons"] = dict()

    return table


def extract_api_data(mappings, section_object):
    """Extract data for verifying the API queries results."""
    table = {}

    for item in mappings:
        value = section_object[item.in_form]

        # Apply same transformations as in `intake_to_dissemination.py`
        if item.type == bool:
            value = Util.bool_to_yes_no(value)
        elif item.type == list:
            value = Util.json_array_to_str(value)

        if item.in_dissem:
            if item.in_dissem == FormFieldInDissem:
                table[item.in_form] = value
            else:
                table[item.in_dissem] = value

    return table
