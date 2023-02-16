import json
import string
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile

from random import choice, randrange

from .test_schemas import FederalAwardsSchemaValidityTest
from .validators import (
    ALLOWED_EXCEL_CONTENT_TYPES,
    validate_excel_filename,
    validate_federal_award_json,
    validate_uei,
    validate_uei_alphanumeric,
    validate_uei_valid_chars,
    validate_uei_leading_char,
    validate_uei_nine_digit_sequences,
)

# Simplest way to create a new copy of simple case rather than getting
# references to things used by other tests:
jsoncopy = lambda v: json.loads(json.dumps(v))


class FederalAwardsValidatorTests(SimpleTestCase):
    """
    We want to make sure that SingleAuditChecklist.federal_awards is going
    through JSON Schema validation, but the full set of JSON Schema tests is in
    test_schemas.py
    """

    def test_validation_is_applied(self):
        """
        Empty Federal Awards should fail, simple case should pass.
        """
        invalid = json.loads("{}")
        expected_msg = "[\"'Federal Awards' is a required property.\"]"
        self.assertRaisesRegex(
            ValidationError, expected_msg, validate_federal_award_json, invalid
        )

        simple = FederalAwardsSchemaValidityTest.SIMPLE_CASE
        validate_federal_award_json(simple)

    def test_prefix_under_ten(self):
        """
        Prefixes between 00 and 09 should fail
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 00 and 09 (invalid)
        prefix = f"{randrange(10):02}"
        # pick an extension beteween 001 and 999 (valid)
        extension = f"{randrange(1, 1000):03}"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        self.assertRaises(ValidationError, validate_federal_award_json, simple)

    def test_prefix_over_99(self):
        """
        Prefixes over 99 should fail
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 100 and 999 (invalid)
        prefix = f"{randrange(100, 1000):03}"
        # pick an extension beteween 001 and 999 (valid)
        extension = f"{randrange(1, 1000):03}"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        self.assertRaises(ValidationError, validate_federal_award_json, simple)

    def test_prefix_non_numeric(self):
        """
        Prefixes with non-numeric characters should fail
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick prefixes that contain one or two non-numeric characters
        prefixes = [
            f"{choice(string.ascii_letters)}{randrange(10):1}",  # e.g. A1
            f"{randrange(10):1}{choice(string.ascii_letters)}",  # e.g. 1A
            f"{choice(string.ascii_letters)}{choice(string.ascii_letters)}",  # e.g. AA
        ]

        # pick an extension between 001 and 999 (valid)
        extension = f"{randrange(1, 1000):03}"

        for prefix in prefixes:
            with self.subTest():
                simple["FederalAwards"]["federal_awards"][0][
                    "program_number"
                ] = f"{prefix}.{extension}"

                self.assertRaises(ValidationError, validate_federal_award_json, simple)

    def test_extension_RD(self):
        """
        A CFDA extension of RD should pass
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 100):02}"
        # use RD as extension (valid)
        extension = "RD"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        validate_federal_award_json(simple)

    def test_extension_U(self):
        """
        A CFDA extension of U## should pass
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 100):02}"
        # pick an extension between U10 and U99 (valid)
        extension = f"U{randrange(10, 100):02}"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        validate_federal_award_json(simple)

    def test_extension_U_single_digit(self):
        """
        A CFDA extension of U# should fail
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 100):02}"
        # pick an extension between U0 and U9
        extension = f"U{randrange(10):1}"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        self.assertRaises(ValidationError, validate_federal_award_json, simple)

    def test_extension_U_three_digit(self):
        """
        A CFDA extension of U### should fail
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 100):02}"
        # pick an extension between U001 and U999
        extension = f"U{randrange(1000):03}"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        self.assertRaises(ValidationError, validate_federal_award_json, simple)

    def test_three_digit_extension(self):
        """
        A three digit numeric CFDA extension should pass
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 100):02}"
        # pick an extension between 001 and 999 (valid)
        extension = f"{randrange(1, 1000):03}"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        validate_federal_award_json(simple)

    def test_four_plus_extension(self):
        """
        A CFDA extension with four digits should fail
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 100):02}"
        # pick an extension with four or more digits
        extension = f"{randrange(1000):04}"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        self.assertRaises(ValidationError, validate_federal_award_json, simple)

    def test_trailing_extension_letter(self):
        """
        A CFDA extension with 3 numeric digits and a trailing letter should pass
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 100):02}"
        # pick an extension between 001 and 999 with a trailing letter (valid)
        extension = f"{randrange(1, 1000):03}{choice(string.ascii_letters)}"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        validate_federal_award_json(simple)

    def test_trailing_extension_letters(self):
        """
        A CFDA extension with 3 numeric digits and multiple trailing letters should fail
        """
        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 100):02}"
        # pick an extension between 001 and 999 with 2 trailing letters (invalid)
        extension = f"{randrange(1, 1000):03}{choice(string.ascii_letters)}{choice(string.ascii_letters)}"

        simple["FederalAwards"]["federal_awards"][0][
            "program_number"
        ] = f"{prefix}.{extension}"

        self.assertRaises(ValidationError, validate_federal_award_json, simple)

    def test_extension_non_numeric(self):
        """
        Extensions with non-numeric characters (except RD, U##, and trailing letter) should fail
        """
        ascii_letters_omit_RD = string.ascii_letters.replace("D", "").replace("R", "")
        ascii_letters_omit_U = string.ascii_letters.replace("U", "")

        simple = jsoncopy(FederalAwardsSchemaValidityTest.SIMPLE_CASE)

        # pick a prefix between 10 and 99 (valid)
        prefix = f"{randrange(10, 100):02}"

        # pick extensions with one or more non-numeric characters
        extensions = [
            f"{choice(string.ascii_letters)}",  # e.g. A
            f"{choice(ascii_letters_omit_RD)}{choice(ascii_letters_omit_RD)}",  # e.g. AB
            f"{choice(string.ascii_letters)}{choice(string.ascii_letters)}{choice(string.ascii_letters)}",  # e.g. ABC
            f"{choice(ascii_letters_omit_U)}{randrange(100):02}",  # e.g. A01
            f"{choice(string.ascii_letters)}{choice(string.ascii_letters)}{randrange(10):1}",  # e.g. AB1
        ]

        for extension in extensions:
            with self.subTest():
                simple["FederalAwards"]["federal_awards"][0][
                    "program_number"
                ] = f"{prefix}.{extension}"

                self.assertRaises(ValidationError, validate_federal_award_json, simple)


class UEIValidatorTests(SimpleTestCase):
    """
    This is for local and pattern-based validation only; this does not perform
    any external queries to verify that given UEIs exist in the world.
    """

    # Valid UEI
    valid = "ABC123DEF456"

    def test_uei(self):
        """UEI is valid using all tests"""
        invalid = "000000000000"

        # Invalid UEI
        self.assertRaises(ValidationError, validate_uei, invalid)
        # Valid UEI
        validate_uei(self.valid)

    def test_uei_is_alphanumeric_only(self):
        """UEI is alphanumeric only"""
        invalid = "!@#123ABC456"

        # Invalid UEI
        self.assertRaises(ValidationError, validate_uei_alphanumeric, invalid)
        # Valid UEI
        validate_uei(self.valid)

    def test_uei_does_not_contain_o_or_i(self):
        """UEI does not contain O or I"""
        contains_o = "ABCo123"
        contains_O = "ABCO123"
        contains_i = "ABC0i23"
        contains_I = "ABC0I23"

        # UEI with o
        self.assertRaises(ValidationError, validate_uei_valid_chars, contains_o)
        # UEI with O
        self.assertRaises(ValidationError, validate_uei_valid_chars, contains_O)
        # UEI with i
        self.assertRaises(ValidationError, validate_uei_valid_chars, contains_i)
        # UEI with I
        self.assertRaises(ValidationError, validate_uei_valid_chars, contains_I)
        # Valid UEI
        validate_uei_valid_chars(self.valid)

    def test_uei_does_not_start_with_0(self):
        """UEI does not start with 0"""
        invalid = "012345678901"

        # UEI starts with O
        self.assertRaises(ValidationError, validate_uei_leading_char, invalid)
        # Valid UEI
        validate_uei_leading_char(self.valid)

    def test_uei_does_not_contain_9_digit_sequence(self):
        """UEI does not contain 9 digit sequence"""
        invalid = "12345678901"

        # UEI contains 9 digit sequence
        self.assertRaises(ValidationError, validate_uei_nine_digit_sequences, invalid)
        # Valid UEI
        validate_uei_nine_digit_sequences(self.valid)


class ExcelFileValidatorTests(SimpleTestCase):
    def test_valid_filename_slug(self):
        """
        Filenames that can be slugified are valid
        """
        test_cases = [
            ("this one just has spaces.xlsx", "this-one-just-has-spaces.xlsx"),
            ("this_one\ has some? other things!.xlsx", "this-one-has-some-other-things.xlsx"),
            ("this/one/has/forward/slashes.xlsx", "slashes.xlsx"),
            ("this.one.has.multiple.extensions.xlsx", "this-one-has-multiple-extensions.xlsx"),
        ]

        for test_case in test_cases:
            with self.subTest():
                before, after = test_case
                valid_file = TemporaryUploadedFile(before, ALLOWED_EXCEL_CONTENT_TYPES[0], 10000, "utf-8")

                validated_filename = validate_excel_filename(valid_file)

                self.assertEqual(validated_filename, after)

    def test_invalid_filename_slug(self):
        """
        Filenames that cannot be slugified are not valid
        """
        test_cases = [
            "no-extension",
            ".xlsx",
            "".join(choice(string.punctuation) for i in range(1, 9)),
            "".join(choice(string.punctuation) for i in range(1, 9)) + ".xlsx"
        ]

        for test_case in test_cases:
            with self.subTest():
                file = TemporaryUploadedFile(test_case, ALLOWED_EXCEL_CONTENT_TYPES[0], 10000, "utf-8")
                
                self.assertRaises(ValidationError, validate_excel_filename, file)
