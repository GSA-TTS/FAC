from django.test import SimpleTestCase

from .update_program_data import extract, transform, update_json, PROGRAM_EXPR


class UpdateProgramDataTest(SimpleTestCase):
    def test_extract_empty_input(self):
        """
        If the input data is an empty array, the returned data should be an empty array
        """
        result = extract([])

        self.assertEqual(result, [])

    def test_extract_missing_headers(self):
        """
        If the input data is missing either the Program Title or ProgramNumber columns, an error should be raised
        """
        self.assertRaises(
            KeyError, extract, ["Not Program Title,ProgramNumber", "test-title,123.456"]
        )
        self.assertRaises(
            KeyError, extract, ["Program Title,NotProgramNumber", "test-title,123.456"]
        )

    def test_extract_no_data_rows(self):
        """
        If the input data has header rows but no data rows, the returned data should be an empty array
        """
        result = extract(["Program Title,ProgramNumber"])

        self.assertEqual(result, [])

    def test_extract_simple_case(self):
        """
        Extract should pull pairs of program names and number from the CSV input and return them as an array of objects
        """
        result = extract(["Program Title,Program Number", "test-title,123.456"])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["program_name"], "test-title")
        self.assertEqual(result[0]["program_number"], "123.456")

    def test_transform_empty_input(self):
        """
        If no program data is provided, the returned schema definition should have an empty array for its anyOf property
        """
        result = transform([])

        self.assertEqual(result["title"], "ProgramNumber")
        self.assertEqual(result["type"], "string")
        self.assertEqual(result["description"], "Program numbers")
        self.assertEqual(result["anyOf"], [])

    def test_transform_simple_case(self):
        """
        The provided program_data should be transformed into a JSON schema definition
        """
        result = transform(
            [{"program_name": "test-title", "program_number": "123.456"}]
        )

        self.assertEqual(result["title"], "ProgramNumber")
        self.assertEqual(result["type"], "string")
        self.assertEqual(result["description"], "Program numbers")
        self.assertEqual(
            result["anyOf"], [{"const": "123.456", "description": "test-title"}]
        )

    def test_load_bad_schema(self):
        """
        If the schema provided does not contain a ProgramNumber definition, the load function should be a no-op
        """
        schema = {"$defs": {}}
        schema_def = {"type": "test"}

        result = update_json(schema, PROGRAM_EXPR, schema_def)

        self.assertEqual(result, schema)

    def test_load_simple_case(self):
        """
        If the schema provided does contain a ProgramNumber definition, it should be overwritten with the provided schema_def
        """
        schema = {"$defs": {"ProgramNumber": {"type", "old"}}}
        schema_def = {"type": "new"}
        expected_result = {"$defs": {"ProgramNumber": schema_def}}

        result = update_json(schema, PROGRAM_EXPR, schema_def)

        self.assertEqual(result, expected_result)
