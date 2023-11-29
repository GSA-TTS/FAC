from django.test import SimpleTestCase
from .exception_utils import DataMigrationError

from .workbooklib.notes_to_sefa import xform_is_minimis_rate_used


class TestXformIsMinimisRateUsed(SimpleTestCase):
    def test_rate_used(self):
        """Test that the function returns 'Y' when the rate is used."""
        self.assertEqual(
            xform_is_minimis_rate_used("The auditee  used the de minimis cost rate."),
            "Y",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The School has elected to use the 10-percent de minimis indirect cost rate as allowed under the Uniform Guidance."
            ),
            "Y",
        )

    def test_rate_not_used(self):
        """Test that the function returns 'N' when the rate is not used."""
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The auditee did not use the de minimis cost rate."
            ),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The Board has elected not to use the 10 percent de minimus indirect cost as allowed under the Uniform Guidance."
            ),
            "N",
        )

    def test_ambiguous_or_unclear_raises_exception(self):
        """Test that the function raises an exception when rate usage is ambiguous or unclear."""
        with self.assertRaises(DataMigrationError):
            xform_is_minimis_rate_used(
                "The information regarding the de minimis rate is not clear."
            )

        with self.assertRaises(DataMigrationError):
            xform_is_minimis_rate_used(
                "It is unknown whether the de minimis rate was applied."
            )
