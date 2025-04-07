from django.test import TestCase
from audit.models import Access, Audit
from .audit_validation_shape import audit_validation_shape
from .check_certifying_contacts import check_certifying_contacts
from .errors import err_certifying_contacts_should_not_match

from model_bakery import baker


class CheckCertifyingContactsTest(TestCase):
    def setUp(self):
        """Set up the common variables for the test cases."""
        self.email1 = "auditee@example.com"
        self.email2 = "auditor@example.com"
        self.email3 = "same@example.com"

    def _make_audit(self, auditee_email, auditor_email) -> Audit:
        audit = baker.make(Audit, version=0)
        baker.make(
            Access, audit=audit, role="certifying_auditee_contact", email=auditee_email
        )
        baker.make(
            Access, audit=audit, role="certifying_auditor_contact", email=auditor_email
        )

        return audit

    def test_diff_certifying_contacts(self):
        """When auditor and auditee emails are different, no errors should be raised."""
        audit = self._make_audit(self.email1, self.email2)
        errors = check_certifying_contacts(audit_validation_shape(audit))
        self.assertEqual(errors, [])

    def test_same_certifying_contacts_raise_errors(self):
        """When auditor and auditee emails are the same, the appropriate error should be raised."""
        audit = self._make_audit(self.email3, self.email3)
        errors = check_certifying_contacts(audit_validation_shape(audit))

        self.assertEqual(len(errors), 1)

        expected_error = err_certifying_contacts_should_not_match()

        self.assertIn({"error": expected_error}, errors)
