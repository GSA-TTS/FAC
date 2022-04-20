from django.test import SimpleTestCase
from django.core.exceptions import ValidationError

from .validators import validate_uei, validate_uei_valid_chars, validate_uei_leading_char, validate_uei_nine_digit_sequences

# Create your tests here.
class UEIValidatorTests(SimpleTestCase):

    def test_uei(self):
        """UEI is valid using all tests"""
        # Invalid UEI
        self.assertRaises(ValidationError, validate_uei, "000000000000")
        # Valid UEI
        validate_uei("ABC123DEF456")

    def test_uei_does_not_contain_o_or_i(self):
        """UEI does not contain O or I"""
        # UEI with O
        self.assertRaises(ValidationError, validate_uei_valid_chars, "123456789O11")
        # UEI with I
        self.assertRaises(ValidationError, validate_uei_valid_chars, "I23456789011")
        # This should not raise a validation error because it does not have an O or I
        validate_uei_valid_chars("123456789011")
        
    def test_uei_does_not_start_with_0(self):
        """UEI does not start with 0"""
        # UEI starts with O
        self.assertRaises(ValidationError, validate_uei_leading_char, "012345678901")
        # UEI does not start with 0
        validate_uei_leading_char("123456789011")

    def test_uei_does_not_contain_9_digit_sequence(self):
        """UEI does not contain 9 digit sequence"""
        # UEI contains 9 digit sequence
        self.assertRaises(ValidationError, validate_uei_nine_digit_sequences, "12345678901")
        # UEI does not contain 9 digit sequence
        validate_uei_nine_digit_sequences("ABC123DEF456")