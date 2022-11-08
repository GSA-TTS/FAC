from django.test import SimpleTestCase

from .update_program_data import extract, transform


class UpdateProgramDataTest(SimpleTestCase):
    def test_extract_empty_input(self):
        result = extract([])

        self.assertEqual(result, [])

    def test_extract_simple_case(self):
        result = extract(["Program Title,Program Number", "test-title,123.456"])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["program_name"], "test-title")
        self.assertEqual(result[0]["program_number"], "123.456")

    def test_transform_empty_input(self):
        result = transform([])

        self.assertEqual(result["title"], "ProgramNumber")
        self.assertEqual(result["type"], "string")
        self.assertEqual(result["description"], "Program numbers")
        self.assertEqual(result["anyOf"], [])

    def test_transform_simple_case(self):
        result = transform(
            [{"program_name": "test-title", "program_number": "123.456"}]
        )

        self.assertEqual(result["title"], "ProgramNumber")
        self.assertEqual(result["type"], "string")
        self.assertEqual(result["description"], "Program numbers")
        self.assertEqual(
            result["anyOf"], [{"const": "123.456", "description": "test-title"}]
        )
