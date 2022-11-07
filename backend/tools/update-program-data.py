import argparse
import csv
import json

from jsonpath_ng import parse


def extract(input_filename):
    data = []
    with open(input_filename, encoding="cp1252") as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            data.append({
                "program_name": row[0],
                "program_number": row[1]
            })
    
    return data


def transform(program_data):
    schema = {
        "title": "ProgramNumber",
        "type": "string",
        "description": "Program numbers",
        "anyOf": []
    }

    for entry in program_data:
        schema["anyOf"].append({
            "const": entry["program_number"],
            "description": entry["program_name"]
        })

    return schema


def load(schema_filename, schema_def):
    with open(schema_filename) as schema_file:
        schema = json.load(schema_file)

        jsonpath_expr = parse("$.\"$defs\".ProgramNumber")
        jsonpath_expr.update(schema, schema_def)

        return schema


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input-filename", type=str, required=True, help="Filename for assistance listings CSV file from SAM.gov")
    parser.add_argument("--schema-filename", type=str, required=True, help="Filename for the JSON schema to be updated")
    parser.add_argument("--output-filename", type=str, required=False, help="[Optional] Filename for the updated JSON schema. If not present, schema-filename will be updated in place")

    args = parser.parse_args()

    program_data = extract(args.input_filename)
    schema_def = transform(program_data)
    updated_schema = load(args.schema_filename, schema_def)

    output_filename = args.output_filename or args.schema_filename

    with open(output_filename, 'w') as schema_file:
        json.dump(updated_schema, schema_file, indent=2)


if __name__ == "__main__":
    main()
