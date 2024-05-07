from django.test import SimpleTestCase
from django.conf import settings
from .workbooklib.secondary_auditors import xform_cpafirmname


class TestXformCpaFirmName(SimpleTestCase):
    class MockSecondaryAuditorHeader:
        def __init__(
            self,
            DBKEY,
            CPAFIRMNAME,
        ):
            self.DBKEY = DBKEY
            self.CPAFIRMNAME = CPAFIRMNAME

    def _mock_secondaryauditor_header(self):
        """Returns a mock secondary_auditor with all necessary fields."""
        return self.MockSecondaryAuditorHeader(
            DBKEY="123456789",
            CPAFIRMNAME="John Doe CPA Firm",
        )

    def test_valid_cpafirm(self):
        """Test that the function returns the valid CPAFIRMNAME."""
        secondary_auditor = self._mock_secondaryauditor_header()
        result = xform_cpafirmname(secondary_auditor)
        self.assertEqual(result.CPAFIRMNAME, secondary_auditor.CPAFIRMNAME)

    def test_blank_cpafirm(self):
        """Test that the function returns GSA_MIGRATION for CPAFIRMNAME."""
        secondary_auditor = self._mock_secondaryauditor_header()
        secondary_auditor.CPAFIRMNAME = ""
        result = xform_cpafirmname(secondary_auditor)
        self.assertEqual(result.CPAFIRMNAME, settings.GSA_MIGRATION)
