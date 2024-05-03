from django.test import SimpleTestCase

from .base_field_maps import FormFieldInDissem, FormFieldMap
from .exception_utils import (
  DataMigrationError,
  DataMigrationValueError,
)
from .sac_general_lib.utils import (
    create_json_from_db_object,
    normalize_year_string_or_exit,
)
from .transforms.xform_remove_hyphen_and_pad_zip import xform_remove_hyphen_and_pad_zip
from .transforms.xform_string_to_bool import string_to_bool
from .transforms.xform_string_to_int import string_to_int
from .transforms.xform_string_to_string import string_to_string
from .transforms.xform_uppercase_y_or_n import uppercase_y_or_n


class TestCreateJsonFromDbObject(SimpleTestCase):
    """Tests for the create_json_from_db_object function."""

    class MockDBObject:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    mappings = [
        FormFieldMap(
            "first_field_name", "IN_DB_FIRST_FIELD", FormFieldInDissem, "", str
        ),
        FormFieldMap(
            "second_field_name", "IN_DB_SECOND_FIELD", FormFieldInDissem, None, bool
        ),
        FormFieldMap("third_field_name", None, FormFieldInDissem, "default_value", str),
    ]

    def test_normal_case(self):
        """Test that the function returns the correct JSON."""
        db_obj = self.MockDBObject(IN_DB_FIRST_FIELD="John", IN_DB_SECOND_FIELD="Y")
        expected_json = {
            "first_field_name": "John",
            "second_field_name": True,
            "third_field_name": "default_value",
        }
        self.assertEqual(
            create_json_from_db_object(db_obj, self.mappings), expected_json
        )

    def test_missing_field(self):
        """
        Test the function for correct JSON output when a database field is missing and the mapping has no default value.
        """
        # In this case, second_field_name is not returned because the mapping for this field has no default value.
        # and the value of the database field `IN_DB_SECOND_FIELD` is missing.
        # `third_field_name` is returned because it has a default value of `default_value`
        db_obj = self.MockDBObject(IN_DB_FIRST_FIELD="John")
        expected_json = {
            "first_field_name": "John",
            "third_field_name": "default_value",
        }
        self.assertEqual(
            create_json_from_db_object(db_obj, self.mappings), expected_json
        )

    def test_none_value(self):
        """Test the function for correct JSON output when a database field has a value of None."""
        db_obj = self.MockDBObject(IN_DB_FIRST_FIELD=None, IN_DB_SECOND_FIELD=None)
        # In this case, second_field_name is not returned because the mapping for this field has no default value.
        # and the value of the database field `IN_DB_SECOND_FIELD` is None.
        # `third_field_name` is returned because it has a default value of `default_value`
        # `first_field_name` is returned because it has a default value of `""`.
        expected_json = {"third_field_name": "default_value"}
        self.assertEqual(
            create_json_from_db_object(db_obj, self.mappings), expected_json
        )

    def test_all_default_values(self):
        """Test the function for correct JSON output when all database fields have default values."""
        db_obj = self.MockDBObject()
        # In this case, second_field_name is not returned because the mapping for this field has no default value.
        # and the value of the database field `IN_DB_SECOND_FIELD` is None.
        # `third_field_name` is returned because it has a default value of `default_value`
        # `first_field_name` is returned because it has a default value of `""`.
        expected_json = {"first_field_name": "", "third_field_name": "default_value"}
        self.assertEqual(
            create_json_from_db_object(db_obj, self.mappings), expected_json
        )


class TestStringToBool(SimpleTestCase):
    """Tests for the string_to_bool function."""

    def test_valid_boolean_string(self):
        self.assertTrue(string_to_bool("Y"))
        self.assertTrue(string_to_bool("y"))
        self.assertFalse(string_to_bool("N"))
        self.assertFalse(string_to_bool("n"))

    def test_string_with_spaces(self):
        self.assertTrue(string_to_bool(" Y "))
        self.assertFalse(string_to_bool("  n"))

    def test_empty_string(self):
        with self.assertRaises(DataMigrationValueError):
            string_to_bool("")

    def test_non_string_input(self):
        with self.assertRaises(DataMigrationValueError):
            string_to_bool(123)
        with self.assertRaises(DataMigrationValueError):
            string_to_bool(None)
        with self.assertRaises(DataMigrationValueError):
            string_to_bool(["True"])
        with self.assertRaises(DataMigrationValueError):
            string_to_bool(True)

    def test_string_length_more_than_one(self):
        with self.assertRaises(DataMigrationValueError):
            string_to_bool("Yes")
        with self.assertRaises(DataMigrationValueError):
            string_to_bool("No")

    def test_invalid_single_character_string(self):
        with self.assertRaises(DataMigrationValueError):
            string_to_bool("A")
        with self.assertRaises(DataMigrationValueError):
            string_to_bool("Z")

class TestUppercaseYOrN(SimpleTestCase):
    """Tests for the uppercase_y_or_n function."""

    def test_valid_boolean_string(self):
        self.assertEqual(uppercase_y_or_n("Y"), "Y")
        self.assertEqual(uppercase_y_or_n("y"), "Y")
        self.assertEqual(uppercase_y_or_n("N"), "N")
        self.assertEqual(uppercase_y_or_n("n"), "N")

    def test_string_with_spaces(self):
        self.assertEqual(uppercase_y_or_n(" Y "), "Y")
        self.assertEqual(uppercase_y_or_n("  n"), "N")

    def test_empty_string(self):
        with self.assertRaises(DataMigrationValueError):
            uppercase_y_or_n("")

    def test_non_string_input(self):
        with self.assertRaises(DataMigrationValueError):
            uppercase_y_or_n(123)
        with self.assertRaises(DataMigrationValueError):
            uppercase_y_or_n(None)
        with self.assertRaises(DataMigrationValueError):
            uppercase_y_or_n(["True"])
        with self.assertRaises(DataMigrationValueError):
            uppercase_y_or_n(True)

    def test_string_length_more_than_one(self):
        with self.assertRaises(DataMigrationValueError):
            uppercase_y_or_n("Yes")
        with self.assertRaises(DataMigrationValueError):
            uppercase_y_or_n("No")

    def test_invalid_single_character_string(self):
        with self.assertRaises(DataMigrationValueError):
            uppercase_y_or_n("A")
        with self.assertRaises(DataMigrationValueError):
            uppercase_y_or_n("Z")


class TestStringToInt(SimpleTestCase):
    """Tests for the string_to_int function."""

    def test_valid_integer_strings(self):
        self.assertEqual(string_to_int("123"), 123)
        self.assertEqual(string_to_int("-456"), -456)
        self.assertEqual(string_to_int("   789   "), 789)

    def test_invalid_strings(self):
        with self.assertRaises(DataMigrationValueError):
            string_to_int("abc")
        with self.assertRaises(DataMigrationValueError):
            string_to_int("123abc")
        with self.assertRaises(DataMigrationValueError):
            string_to_int("12.34")

    def test_empty_string(self):
        with self.assertRaises(DataMigrationValueError):
            string_to_int("")

    def test_non_string_input(self):
        with self.assertRaises(DataMigrationValueError):
            string_to_int(123)
        with self.assertRaises(DataMigrationValueError):
            string_to_int(None)
        with self.assertRaises(DataMigrationValueError):
            string_to_int([123])


class TestStringToString(SimpleTestCase):
    def test_valid_strings(self):
        self.assertEqual(string_to_string("hello"), "hello")
        self.assertEqual(string_to_string("  world  "), "world")
        self.assertEqual(string_to_string("  space both sides  "), "space both sides")

    def test_none_input(self):
        self.assertEqual(string_to_string(None), "")

    def test_non_string_input(self):
        with self.assertRaises(DataMigrationValueError):
            string_to_string(123)
        with self.assertRaises(DataMigrationValueError):
            string_to_string(True)
        with self.assertRaises(DataMigrationValueError):
            string_to_string([1, 2, 3])

    def test_string_with_only_spaces(self):
        self.assertEqual(string_to_string("     "), "")


class TestNormalizeYearString(SimpleTestCase):
    def test_valid_short_year(self):
        self.assertEqual(normalize_year_string_or_exit("21"), "2021")
        self.assertEqual(normalize_year_string_or_exit("16"), "2016")

    def test_valid_full_year(self):
        self.assertEqual(normalize_year_string_or_exit("2018"), "2018")

    def test_invalid_year_string(self):
        with self.assertRaises(SystemExit):
            normalize_year_string_or_exit("invalid")

    def test_year_out_of_range(self):
        with self.assertRaises(SystemExit):
            normalize_year_string_or_exit("15")
        with self.assertRaises(SystemExit):
            normalize_year_string_or_exit("2023")


class TestXformAddHyphenToZip(SimpleTestCase):
    def test_five_digit_zip(self):
        self.assertEqual(xform_remove_hyphen_and_pad_zip("12345"), "12345")

    def test_nine_digit_zip(self):
        self.assertEqual(xform_remove_hyphen_and_pad_zip("123456789"), "123456789")

    def test_hyphenated_zip(self):
        self.assertEqual(xform_remove_hyphen_and_pad_zip("12345-6789"), "123456789")
        self.assertEqual(xform_remove_hyphen_and_pad_zip("1234-6789"), "012346789")

    def test_four_digit_zip(self):
        self.assertEqual(xform_remove_hyphen_and_pad_zip("1234"), "01234")

    def test_eight_digit_zip(self):
        self.assertEqual(xform_remove_hyphen_and_pad_zip("12345678"), "012345678")

    def test_malformed_zip(self):
        with self.assertRaises(DataMigrationError):
            xform_remove_hyphen_and_pad_zip("123")
        with self.assertRaises(DataMigrationError):
            xform_remove_hyphen_and_pad_zip("1234-678")
