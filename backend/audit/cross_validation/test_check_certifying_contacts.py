from django.test import TestCase
from audit.models import Access, SingleAuditChecklist
from .sac_validation_shape import sac_validation_shape
from .check_certifying_contacts import check_certifying_contacts
from .errors import err_certifying_contacts_should_not_match

from model_bakery import baker


class CheckCertifyingContactsTest(TestCase):
    def setUp(self):
        """Set up the common variables for the test cases."""
        self.email1 = "auditee@example.com"
        self.email2 = "auditor@example.com"
        self.email3 = "same@example.com"

    def _make_sac(self, auditee_email, auditor_email) -> SingleAuditChecklist:
        sac = baker.make(SingleAuditChecklist)
        baker.make(
            Access, sac=sac, role="certifying_auditee_contact", email=auditee_email
        )
        baker.make(
            Access, sac=sac, role="certifying_auditor_contact", email=auditor_email
        )

        return sac

    def test_diff_certifying_contacts(self):
        """When auditor and auditee emails are different, no errors should be raised."""
        sac = self._make_sac(self.email1, self.email2)
        errors = check_certifying_contacts(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_same_certifying_contacts_raise_errors(self):
        """When auditor and auditee emails are the same, the appropriate error should be raised."""
        sac = self._make_sac(self.email3, self.email3)
        errors = check_certifying_contacts(sac_validation_shape(sac))

        self.assertEqual(len(errors), 1)

        expected_error = err_certifying_contacts_should_not_match()

        self.assertIn({"error": expected_error}, errors)
