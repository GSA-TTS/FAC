from django.conf import settings
from django.test import SimpleTestCase

from census_historical_migration.change_record import InspectionRecord

from .workbooklib.secondary_auditors import (
    xform_address_state,
    xform_address_zipcode,
    xform_cpafirmname,
    xform_pad_contact_phone_with_nine,
)


class TestXformSecondaryAuditorsState(SimpleTestCase):
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


class TestXformSecondaryAuditorsZipcode(SimpleTestCase):
    class SecondaryAuditor:
        def __init__(self, zipcode):
            self.CPAZIPCODE = zipcode

    def test_normal_address_zipcode(self):
        # Setup specific test data
        secondary_auditors = [
            self.SecondaryAuditor("10108"),
        ]

        xform_address_zipcode(secondary_auditors)

        self.assertEqual(secondary_auditors[0].CPAZIPCODE, "10108")

    def test_missing_address_zipcode(self):
        # Setup specific test data
        secondary_auditors = [
            self.SecondaryAuditor(""),
        ]

        xform_address_zipcode(secondary_auditors)

        self.assertEqual(secondary_auditors[0].CPAZIPCODE, settings.GSA_MIGRATION)


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


class TestXformPadContactPhoneWithNine(SimpleTestCase):

    class MockSecondaryAuditorHeader:

        def __init__(
            self,
            CPAPHONE,
        ):
            self.CPAPHONE = CPAPHONE

    def setUp(self):
        self.secondary_auditors = [
            self.MockSecondaryAuditorHeader(CPAPHONE="12345"),
            self.MockSecondaryAuditorHeader(CPAPHONE="999999999"),
            self.MockSecondaryAuditorHeader(CPAPHONE="1234567890"),
            self.MockSecondaryAuditorHeader(CPAPHONE="98765432"),
        ]

    def test_pad_contact_phone(self):
        xform_pad_contact_phone_with_nine(self.secondary_auditors)

        self.assertEqual(self.secondary_auditors[0].CPAPHONE, "12345")  # No change
        self.assertEqual(
            self.secondary_auditors[1].CPAPHONE, "9999999999"
        )  # Pad applied
        self.assertEqual(self.secondary_auditors[2].CPAPHONE, "1234567890")  # No change
        self.assertEqual(self.secondary_auditors[3].CPAPHONE, "98765432")  # No change

    def test_change_records(self):
        secondary_auditors = [self.MockSecondaryAuditorHeader(CPAPHONE="999999999")]
        change_records_before = len(InspectionRecord.change["secondary_auditor"])

        xform_pad_contact_phone_with_nine(secondary_auditors)

        change_records_after = len(InspectionRecord.change["secondary_auditor"])
        self.assertEqual(change_records_after, change_records_before + 1)
