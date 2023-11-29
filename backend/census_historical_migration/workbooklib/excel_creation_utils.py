from census_historical_migration.transforms.xform_string_to_string import (
    string_to_string,
)
from census_historical_migration.transforms.xform_string_to_int import string_to_int
from census_historical_migration.exception_utils import DataMigrationError
from census_historical_migration.base_field_maps import WorkbookFieldInDissem
from census_historical_migration.workbooklib.templates import sections_to_template_paths
from census_historical_migration.sac_general_lib.report_id_generator import (
    dbkey_to_report_id,
    xform_dbkey_to_report_id,
)
from census_historical_migration.models import (
    ELECAUDITS as Audits,
    ELECAUDITHEADER as AuditHeader,
)

from openpyxl.utils.cell import (
    rows_from_range,
    coordinate_from_string,
    column_index_from_string,
)

import sys
import logging


logger = logging.getLogger(__name__)


def set_range(wb, range_name, values, default=None, conversion_fun=str):
    """
    Helper to set a range of values. Takes a named range, and then walks down
    the range, filling in the given values.

    wb (Workbook)       The workbook
    range_name (string) Name of the range to set
    values (iterable)   Values to set within the range
    default (any)       Default value to use; defaults to None.
    conversion (func)   Conversion function to apply to individual values; defaults to str().
    """
    the_range = wb.defined_names[range_name]
    dests = the_range.destinations

    sheet_title, coord = None, None
    for cur_sheet_title, cur_coord in dests:
        if sheet_title or coord:
            # `destinations` is meant to be iterated over, but we only expect one value
            raise ValueError(f"{range_name} has more than one destination")
        else:
            sheet_title, coord = cur_sheet_title, cur_coord

    ws = None
    try:
        ws = wb[sheet_title]
    except KeyError:
        raise KeyError(f"Sheet title '{sheet_title}' not found in workbook")

    values = list(values)
    for i, row in enumerate(rows_from_range(coord)):
        # Iterate over the rows, but stop when we run out of values
        value = None
        try:
            value = values[i]
        except IndexError:
            break

        # Get the row and column to set the current value
        cell = row[0]  # [('B12',)] -> ('B12',)
        col_str, row = coordinate_from_string(cell)  # ('B12',) -> 'B', 12
        col = column_index_from_string(col_str)  # 'B' -> 2

        # Check for the type and apply the correct conversion method
        converted_value = apply_conversion_function(value, default, conversion_fun)
        # Set the value of the cell
        ws.cell(row=row, column=col, value=converted_value)


def apply_conversion_function(value, default, conversion_function):
    """
    Helper to apply a conversion function to a value, or use a default value
    """
    if value:
        if conversion_function is str:
            new_value = string_to_string(value)
        elif conversion_function is int:
            new_value = string_to_int(value)
        else:
            new_value = conversion_function(value)
    else:
        new_value = default or ""
    return new_value


def get_range_values(ranges, name):
    """
    Helper to get the values linked to a particular range, identified by its name."""
    for item in ranges:
        if item["name"] == name:
            return item["values"]
    return None


def get_ranges(mappings, values):
    """
    Helper to get range of values.The method iterates over a collection of mappings, applying a conversion
    function to constructs a list of dictionaries, each containing a name and a list of
    transformed values."""
    ranges = []
    for mapping in mappings:
        ranges.append(
            {
                "name": mapping.in_sheet,
                "values": list(
                    map(
                        lambda v: apply_conversion_function(
                            getattr(v, mapping.in_db),
                            mapping.default,
                            mapping.type,
                        ),
                        values,
                    )
                ),
            }
        )
    return ranges


# FIXME-MSHD: Remove this function once we switch all workbook generators to using census models
def set_uei(Gen, wb, dbkey):
    g = Gen.select().where(Gen.dbkey == dbkey).get()
    if g.uei:
        set_range(wb, "auditee_uei", [g.uei])
    else:
        raise DataMigrationError(f"UEI is not set for this audit: {dbkey}")
    return g


def set_workbook_uei(workbook, uei):
    """Sets the UEI value in the workbook's designated UEI cell"""
    if not uei:
        raise DataMigrationError("UEI value is missing or invalid.")
    set_range(workbook, "auditee_uei", [uei])


def get_audit_header(dbkey):
    """Returns the AuditHeader instance for the given dbkey."""
    try:
        audit_header = AuditHeader.objects.get(DBKEY=dbkey)
    except AuditHeader.DoesNotExist:
        raise DataMigrationError(f"No audit header record found for dbkey: {dbkey}")
    return audit_header


def map_simple_columns(wb, mappings, values):
    len_passed_in = len(mappings)
    unique_fields = set()
    for mapping in mappings:
        unique_fields.add(mapping.in_sheet)
    if len_passed_in != len(unique_fields):
        logger.info(f"unique: {len(unique_fields)} list: {len(mappings)}")
        logger.error(
            "You repeated a field in the mappings: {}".format(
                list(map(lambda m: m.in_sheet, mappings))
            )
        )
        sys.exit(-1)

    # Map all the simple ones
    for m in mappings:
        set_range(
            wb,
            m.in_sheet,
            map(lambda v: getattr(v, m.in_db), values),
            m.default,
            m.type,
        )


def get_template_name_for_section(section):
    """
    Return a workbook template name corresponding to the given section
    """
    if section in sections_to_template_paths:
        template_name = sections_to_template_paths[section].name
        return template_name
    else:
        raise ValueError(f"Unknown section {section}")


def generate_dissemination_test_table(Gen, api_endpoint, dbkey, mappings, objects):
    table = {"rows": list(), "singletons": dict()}
    table["endpoint"] = api_endpoint
    table["report_id"] = (
        dbkey_to_report_id(Gen, dbkey)
        if not isinstance(
            Gen, AuditHeader
        )  # FIXME-MSHD: This hack is necessary until we switch all workbook generators to using census models. We may want to get rid of generate_dissemination_test_table at some point (see comment in generate_federal_awards)
        else xform_dbkey_to_report_id(Gen, dbkey)
    )
    for o in objects:
        test_obj = {}
        test_obj["fields"] = []
        test_obj["values"] = []
        for m in mappings:
            # What if we only test non-null values?
            raw_value = getattr(o, m.in_db, None)
            attribute_value = apply_conversion_function(raw_value, m.default, m.type)
            if (attribute_value is not None) and (attribute_value != ""):
                if m.in_dissem == WorkbookFieldInDissem:
                    # print(f'in_sheet {m.in_sheet} <- {attribute_value}')
                    test_obj["fields"].append(m.in_sheet)
                    # The typing must be applied here as well, as in the case of
                    # type_requirement, it alphabetizes the value...
                    test_obj["values"].append(m.type(attribute_value))
                else:
                    # print(f'in_dissem {m.in_dissem} <- {attribute_value}')
                    test_obj["fields"].append(m.in_dissem)
                    test_obj["values"].append(m.type(attribute_value))

        table["rows"].append(test_obj)
    return table


def get_audits(dbkey):
    return Audits.objects.filter(DBKEY=dbkey).order_by("ID")
