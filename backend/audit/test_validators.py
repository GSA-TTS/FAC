import json
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError

from .test_schemas import SchemaValidityTest
from .validators import (
    validate_federal_award_json,
    validate_uei,
    validate_uei_alphanumeric,
    validate_uei_valid_chars,
    validate_uei_leading_char,
    validate_uei_nine_digit_sequences,
)


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

        simple = SchemaValidityTest.SIMPLE_CASE
        validate_federal_award_json(simple)


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
