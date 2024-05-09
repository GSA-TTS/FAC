from django.conf import settings
from django.test import SimpleTestCase

from .workbooklib.secondary_auditors import (
    xform_address_state,
    xform_address_zipcode,
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
