from django.conf import settings
from django.test import SimpleTestCase

from .workbooklib.secondary_auditors import (
    xform_address_state,
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
