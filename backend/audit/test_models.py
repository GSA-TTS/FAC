from django.test import TestCase

from model_bakery import baker

from .models import Access, SingleAuditChecklist, User


class SingleAuditChecklistTests(TestCase):
    """Model tests"""

    def test_str_is_id_and_uei(self):
        """String representation of SAC instance is #{ID} - UEI({UEI})"""
        sac = baker.make(SingleAuditChecklist)
        self.assertEqual(str(sac), f"#{sac.id} - UEI({sac.auditee_uei})")

    def test_report_id(self):
        """
        Verify:

        -   There is a report_id value
        -   The report_id value consists of:
            -   Four-digit year of start of audit period.
            -   Three-digit char (but without I or O) random.
            -   10-digit numeric (monotonically increasing, but starting from
                0001000001 because the Census numbers are six-digit values. The
                formula for creating this is basically "how many non-legacy
                entries there are in the system plus 1,000,000".
        """
        user = baker.make(User)
        sac = SingleAuditChecklist.objects.create(
            auditee_fiscal_period_start="2022-11-01",
            auditee_fiscal_period_end="2023-11-01",
            met_spending_threshold=True,
            is_usa_based=True,
            submitted_by=user,
            submission_status="in_progress",
        )
        self.assertEqual(len(sac.report_id), 17)
        self.assertEqual(sac.report_id[:4], "2022")
        self.assertIn(sac.report_id[4], "ABCDEFGHJKLMNPQRSTUVWXYZ1234567890")
        self.assertIn(sac.report_id[5], "ABCDEFGHJKLMNPQRSTUVWXYZ1234567890")
        self.assertIn(sac.report_id[6], "ABCDEFGHJKLMNPQRSTUVWXYZ1234567890")
        # This one is a little dubious because it assumes this will always be
        # the first entry in the test database:
        self.assertEqual(sac.report_id[7:], "0001000001")


class AccessTests(TestCase):
    """Model tests"""

    def test_str_is_id_and_uei(self):
        """
        String representation of Access instance is:

            {email} as {role} for {sac}
        """
        access = baker.make(Access)
        expected = f"{access.email} as {access.get_role_display()}"
        self.assertEqual(str(access), expected)
