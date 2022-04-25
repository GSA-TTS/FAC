from operator import contains
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from pkg_resources import invalid_marker

from .validators import validate_uei, validate_uei_alphanumeric, validate_uei_valid_chars, validate_uei_leading_char, validate_uei_nine_digit_sequences

# Create your tests here.
class UEIValidatorTests(SimpleTestCase):

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