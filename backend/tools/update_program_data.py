import argparse
import csv
import json

from jsonpath_ng import parse

PROGRAM_EXPR = '$."$defs".ProgramNumber'


def extract(input_data):
    """Extract each row of the CSV into a dict."""

    def build_row(row):
        return {
            "program_name": row["Program Title"],
            "program_number": row["Program Number"],
        }

    reader = csv.DictReader(input_data)
    return [build_row(row) for row in reader]


def transform(program_data):
    """
    Adding each entry in the program data to the anyOf property of the schema.
    """

    def build_entry(entry):
        return {"const": entry["program_number"], "description": entry["program_name"]}

    schema = {
        "title": "ProgramNumber",
        "type": "string",
        "description": "Program numbers",
        "anyOf": [build_entry(entry) for entry in program_data],
    }

    return schema


def update_json(base, path_expr, json_fragment):
    """
    Given base, find the path given by path_expr and overwrite its value with
    json_fragment.
    """
    jsonpath_expr = parse(path_expr)
    jsonpath_expr.update(base, json_fragment)

    return base


def main(program_expr):
    """
    Entry point for CLI invocation.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input-filename",
        type=str,
        required=True,
        help="Filename for assistance listings CSV file from SAM.gov",
    )
    parser.add_argument(
        "--schema-filename",
        type=str,
        required=True,
        help="Filename for the JSON schema to be updated",
    )
    parser.add_argument(
        "--output-filename",
        type=str,
        required=False,
        help="[Optional] Filename for the updated JSON schema. If not present, schema-filename will be updated in place",
    )

    args = parser.parse_args()

    with open(args.input_filename, encoding="cp1252") as csvfile:
        input_data = csvfile.readlines()
        program_data = extract(input_data)

    subschema = transform(program_data)

    with open(args.schema_filename, encoding="utf-8") as schema_file:
        schema = json.load(schema_file)
        updated_schema = update_json(schema, program_expr, subschema)

    output_filename = args.output_filename or args.schema_filename

    with open(output_filename, "w", encoding="utf-8") as schema_file:
        json.dump(updated_schema, schema_file, indent=2)


if __name__ == "__main__":
    main(PROGRAM_EXPR)
