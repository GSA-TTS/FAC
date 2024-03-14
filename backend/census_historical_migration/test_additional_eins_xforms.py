from django.test import SimpleTestCase

from .workbooklib.additional_eins import xform_remove_trailing_decimal_zero
from .exception_utils import DataMigrationValueError


class TestXformRemoveTrailingDecimalZero(SimpleTestCase):
    def test_with_trailing_decimal_zero(self):
        self.assertEqual(xform_remove_trailing_decimal_zero("12345.0"), "12345")
        self.assertEqual(xform_remove_trailing_decimal_zero("67890.0"), "67890")

    def test_without_trailing_decimal_zero(self):
        self.assertEqual(xform_remove_trailing_decimal_zero("12345"), "12345")
        with self.assertRaises(DataMigrationValueError):
            xform_remove_trailing_decimal_zero("67890.5")

    def test_empty_string(self):
        self.assertEqual(xform_remove_trailing_decimal_zero(""), "")

    def test_non_string_input(self):
        self.assertEqual(xform_remove_trailing_decimal_zero(None), "")
