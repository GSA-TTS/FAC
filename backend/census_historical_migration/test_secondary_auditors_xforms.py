from django.conf import settings
from django.test import SimpleTestCase

from .workbooklib.secondary_auditors import (
    xform_address_state,
    xform_cpafirmname,
)


class TestXformSecondaryAuditors(SimpleTestCase):
    class SecondaryAuditor:
        def __init__(self, state):
            self.CPASTATE = state

    def test_normal_address_state(self):
        # Setup specific test data
        secondary_auditors = [
            self.SecondaryAuditor("CA"),
        ]

        xform_address_state(secondary_auditors)

        self.assertEqual(secondary_auditors[0].CPASTATE, "CA")

    def test_missing_address_state(self):
        # Setup specific test data
        secondary_auditors = [
            self.SecondaryAuditor(""),
        ]

        xform_address_state(secondary_auditors)

        self.assertEqual(secondary_auditors[0].CPASTATE, settings.GSA_MIGRATION)


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
        return [
            self.MockSecondaryAuditorHeader(
                DBKEY="123456789",
                CPAFIRMNAME="John Doe CPA Firm",
            ),
            self.MockSecondaryAuditorHeader(
                DBKEY="223456789",
                CPAFIRMNAME="Jack C CPA Firm",
            ),
        ]

    def test_valid_cpafirm(self):
        """Test that the function does not change the valid CPAFIRMNAME."""
        secondary_auditors = self._mock_secondaryauditor_header()
        cpas = secondary_auditors
        xform_cpafirmname(secondary_auditors)
        for index in range(len(secondary_auditors)):
            self.assertEqual(
                secondary_auditors[index].CPAFIRMNAME, cpas[index].CPAFIRMNAME
            )

    def test_blank_cpafirm(self):
        """Test that the function changes blank CPAFIRMNAME to GSA_MIGRATION."""
        secondary_auditors = self._mock_secondaryauditor_header()
        secondary_auditors[0].CPAFIRMNAME = ""
        cpas = secondary_auditors
        xform_cpafirmname(secondary_auditors)
        self.assertEqual(secondary_auditors[0].CPAFIRMNAME, settings.GSA_MIGRATION)
        self.assertEqual(secondary_auditors[1].CPAFIRMNAME, cpas[1].CPAFIRMNAME)
