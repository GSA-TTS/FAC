from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.test import TestCase

from django_fsm import TransitionNotAllowed
from model_bakery import baker

from .models import Access, ExcelFile, SingleAuditChecklist, User


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
        general_information = {
            "auditee_fiscal_period_start": "2022-11-01",
            "auditee_fiscal_period_end": "2023-11-01",
            "met_spending_threshold": True,
            "is_usa_based": True,
        }
        sac = SingleAuditChecklist.objects.create(
            submitted_by=user,
            submission_status="in_progress",
            general_information=general_information,
        )
        self.assertEqual(len(sac.report_id), 17)
        self.assertEqual(sac.report_id[:4], "2022")
        self.assertIn(sac.report_id[4], "ABCDEFGHJKLMNPQRSTUVWXYZ1234567890")
        self.assertIn(sac.report_id[5], "ABCDEFGHJKLMNPQRSTUVWXYZ1234567890")
        self.assertIn(sac.report_id[6], "ABCDEFGHJKLMNPQRSTUVWXYZ1234567890")
        # This one is a little dubious because it assumes this will always be
        # the first entry in the test database:
        self.assertEqual(sac.report_id[7:], "0001000001")

    def test_submission_status_transitions(self):
        """
        Test that only the expected state transitions are allowed for submission_status
        """
        cases = (
            (
                SingleAuditChecklist.STATUS.IN_PROGRESS,
                SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION,
                "transition_to_ready_for_certification",
            ),
            (
                SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION,
                SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED,
                "transition_to_auditor_certified",
            ),
            (
                SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED,
                SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED,
                "transition_to_auditee_certified",
            ),
            (
                SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED,
                SingleAuditChecklist.STATUS.CERTIFIED,
                "transition_to_certified",
            ),
            (
                SingleAuditChecklist.STATUS.CERTIFIED,
                SingleAuditChecklist.STATUS.SUBMITTED,
                "transition_to_submitted",
            ),
        )

        for status_from, status_to, transition_name in cases:
            sac = baker.make(SingleAuditChecklist, submission_status=status_from)

            transition_method = getattr(sac, transition_name)
            transition_method()

            self.assertEqual(sac.submission_status, status_to)

            bad_statuses = [
                status[0]
                for status in SingleAuditChecklist.STATUS_CHOICES
                if status[0] is not status_from
            ]

            for bad_status in bad_statuses:
                with self.subTest():
                    sac.submission_status = bad_status

                    self.assertRaises(TransitionNotAllowed, transition_method)


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

    def test_multiple_auditee_contacts_allowed(self):
        """
        There should be no constraint preventing multiple auditee contacts for a SAC
        """
        access_1 = baker.make(Access, role="auditee_contact")

        baker.make(Access, sac=access_1.sac, role="auditee_contact")

    def test_multiple_auditor_contacts_allowed(self):
        """
        There should be no constraint preventing multiple auditor contacts for a SAC
        """
        access_1 = baker.make(Access, role="auditor_contact")

        baker.make(Access, sac=access_1.sac, role="auditor_contact")

    def test_multiple_creator_not_allowed(self):
        """
        There should be a constraint preventing multiple creators for a SAC
        """
        access_1 = baker.make(Access, role="creator")

        self.assertRaises(
            IntegrityError, baker.make, Access, sac=access_1.sac, role="creator"
        )

    def test_multiple_certifying_auditee_contact_not_allowed(self):
        """
        There should be a constraint preventing multiple certifying_auditee_contacts for a SAC
        """
        access_1 = baker.make(Access, role="certifying_auditee_contact")

        self.assertRaises(
            IntegrityError,
            baker.make,
            Access,
            sac=access_1.sac,
            role="certifying_auditee_contact",
        )

    def test_multiple_certifying_auditor_contact_not_allowed(self):
        """
        There should be a constraint preventing multiple certifying_auditor_contacts for a SAC
        """
        access_1 = baker.make(Access, role="certifying_auditor_contact")

        self.assertRaises(
            IntegrityError,
            baker.make,
            Access,
            sac=access_1.sac,
            role="certifying_auditor_contact",
        )


class ExcelFileTests(TestCase):
    """Model tests"""

    def test_filename_generated(self):
        """
        The filename field should be generated based on the FileField filename
        """
        file = SimpleUploadedFile("this is a file.xlsx", b"this is a file")

        excel_file = baker.make(ExcelFile, file=file)

        self.assertEqual("this-is-a-file.xlsx", excel_file.filename)
