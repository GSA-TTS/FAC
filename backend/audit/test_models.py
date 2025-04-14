from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.test import TestCase

from viewflow.fsm import TransitionNotAllowed
from model_bakery import baker

from .exceptions import LateChangeError
from .models import Access, ExcelFile, SingleAuditReportFile, History
from audit.models import Audit
from .models.constants import STATUS, AuditType, EventType, STATUS_CHOICES
from .models.viewflow import audit_transition, AuditFlow


class MockRequest:
    user = baker.make(User)


class AuditTests(TestCase):
    """Model tests"""

    def test_str_is_id_and_uei(self):
        """String representation of SAC instance is #{ID} - UEI({UEI})"""
        audit = baker.make(Audit, version=0)
        self.assertEqual(
            str(audit), f"#{audit.id}--{audit.report_id}--{audit.auditee_uei}"
        )

    def test_report_id(self):
        """
        Verify:

        -   There is a report_id value
        -   The report_id value consists of:
            -   Four-digit year based on submission fiscal end date.
            -   Two-digit month based on submission fiscal end date.
            -   Audit source: either GSAFAC or CENSUS.
            -   Zero-padded 10-digit numeric monotonically increasing.
            -   Separated by hyphens.

            For example: `2023-09-GSAFAC-0000000001`, `2020-09-CENSUS-0000000001`.
        """
        user = baker.make(User)
        general_information = {
            "auditee_fiscal_period_start": "2022-11-01",
            "auditee_fiscal_period_end": "2023-11-01",
            "met_spending_threshold": True,
            "is_usa_based": True,
        }
        audit = Audit.objects.create(
            submission_status=STATUS.IN_PROGRESS,
            audit_type=AuditType.SINGLE_AUDIT,
            audit={"general_information": general_information},
            event_user=user,
            event_type=EventType.CREATED,
        )
        self.assertEqual(len(audit.report_id), 25)
        separator = "-"
        year, month, source, count = audit.report_id.split(separator)
        self.assertEqual(year, "2023")
        self.assertEqual(month, "11")
        self.assertEqual(source, "GSAFAC")
        # This one is a little dubious because it assumes this will always be
        # the first entry in the test database:
        self.assertEqual(count, "0000000001")

    def test_submission_status_transitions(self):
        """
        Test that only the expected state transitions are allowed for submission_status
        """
        cases = (
            (
                [STATUS.READY_FOR_CERTIFICATION],
                EventType.AUDITOR_CERTIFICATION_COMPLETED,
                STATUS.AUDITOR_CERTIFIED,
                "transition_to_auditor_certified",
            ),
            (
                [STATUS.AUDITOR_CERTIFIED, STATUS.SUBMITTED],
                EventType.AUDITEE_CERTIFICATION_COMPLETED,
                STATUS.AUDITEE_CERTIFIED,
                "transition_to_auditee_certified",
            ),
            (
                [
                    STATUS.AUDITEE_CERTIFIED,
                ],
                EventType.SUBMITTED,
                STATUS.SUBMITTED,
                "transition_to_submitted",
            ),
            (
                [
                    STATUS.READY_FOR_CERTIFICATION,
                    STATUS.AUDITOR_CERTIFIED,
                    STATUS.AUDITEE_CERTIFIED,
                    STATUS.FLAGGED_FOR_REMOVAL,
                ],
                EventType.UNLOCKED_AFTER_CERTIFICATION,
                STATUS.IN_PROGRESS,
                "transition_to_in_progress_again",
            ),
            (
                [
                    STATUS.IN_PROGRESS,
                    STATUS.READY_FOR_CERTIFICATION,
                    STATUS.AUDITOR_CERTIFIED,
                    STATUS.AUDITEE_CERTIFIED,
                    STATUS.CERTIFIED,
                ],
                EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
                STATUS.FLAGGED_FOR_REMOVAL,
                "transition_to_flagged_for_removal",
            ),
        )

        now = datetime.now(timezone.utc)
        for statuses_from, event, expected_status, transition_name in cases:
            for status_from in statuses_from:
                audit = baker.make(Audit, version=0, submission_status=status_from)

                transition_method = getattr(AuditFlow(audit), transition_name)
                audit_transition(MockRequest(), audit, event=event)

                self.assertEqual(audit.submission_status, expected_status)
                history = (
                    History.objects.filter(report_id=audit.report_id, event=event)
                    .order_by("-updated_at")
                    .first()
                )

                self.assertGreaterEqual(history.updated_at, now)

                bad_statuses = [
                    status[0]
                    for status in STATUS_CHOICES
                    if status[0] not in statuses_from
                ]

                for bad_status in bad_statuses:
                    with self.subTest():
                        audit.submission_status = bad_status

                        self.assertRaises(TransitionNotAllowed, transition_method)

    def test_no_late_changes(self):
        """
        Try to make a change to a submission with a status that isn't
        in_progress and get an expected error.
        """
        bad_statuses = [
            status[0] for status in STATUS_CHOICES if status[0] != STATUS.IN_PROGRESS
        ]

        for status_from in bad_statuses:
            audit = baker.make(
                Audit,
                version=0,
                audit_type="single-audit",
                submission_status=status_from,
            )
            audit.audit_type = "program-specific"
            with self.assertRaises(LateChangeError):
                audit.save()


class AccessTests(TestCase):
    """Model tests"""

    def test_str_is_id_and_uei(self):
        """
        String representation of Access instance is:

            {email} as {role} for {audit}
        """
        audit = baker.make(Audit, version=0)
        access = baker.make(Access, audit=audit)
        expected = f"{access.email} as {access.get_role_display()}"
        self.assertEqual(str(access), expected)

    def test_multiple_auditee_contacts_allowed(self):
        """
        There should be no constraint preventing multiple auditee contacts for an Audit
        """
        audit = baker.make(Audit, version=0)
        access_1 = baker.make(Access, audit=audit, role="auditee_contact")

        baker.make(Access, audit=access_1.audit, role="auditee_contact")

    def test_multiple_auditor_contacts_allowed(self):
        """
        There should be no constraint preventing multiple auditor contacts for an Audit
        """
        audit = baker.make(Audit, version=0)
        access_1 = baker.make(Access, audit=audit, role="auditor_contact")

        baker.make(Access, audit=access_1.audit, role="auditor_contact")

    def test_multiple_certifying_auditee_contact_not_allowed(self):
        """
        There should be a constraint preventing multiple certifying_auditee_contacts for an Audit
        """
        audit = baker.make(Audit, version=0)
        access_1 = baker.make(Access, audit=audit, role="certifying_auditee_contact")

        self.assertRaises(
            IntegrityError,
            baker.make,
            Access,
            audit=access_1.audit,
            role="certifying_auditee_contact",
        )

    def test_multiple_certifying_auditor_contact_not_allowed(self):
        """
        There should be a constraint preventing multiple certifying_auditor_contacts for an Audit
        """
        audit = baker.make(Audit, version=0)
        access_1 = baker.make(Access, audit=audit, role="certifying_auditor_contact")

        self.assertRaises(
            IntegrityError,
            baker.make,
            Access,
            audit=access_1.audit,
            role="certifying_auditor_contact",
        )

    def test_access_creation_non_unique_emails(self):
        """
        If we attempt to create an Access for an email that has
        multiple User objects associated with it, we should not
        assign the Access to any specific User object and instead
        leave the Access unclaimed. This way, the next time the
        user logs into the FAC, the Access will be claimed by
        whichever User account is the "active" one.
        """
        creator = baker.make(User)

        baker.make(User, email="a@a.com")
        baker.make(User, email="a@a.com")

        audit = baker.make(Audit, version=0, audit_type="single-audit")
        access = Access.objects.create(
            audit=audit,
            role="editor",
            email="a@a.com",
            event_user=creator,
            event_type=EventType.ACCESS_GRANTED,
        )

        self.assertEqual(access.email, "a@a.com")
        self.assertIsNone(access.user)


class ExcelFileTests(TestCase):
    """Model tests"""

    def test_filename_generated(self):
        """
        The filename field should be generated based on the FileField filename
        """
        file = SimpleUploadedFile("this is a file.xlsx", b"this is a file")
        report_id = "FAKE_REPORT_ID"
        audit = baker.make(Audit, report_id=report_id, version=0)
        excel_file = baker.make(
            ExcelFile, file=file, form_section="sectionname", audit=audit
        )

        self.assertEqual(f"{report_id}--sectionname.xlsx", excel_file.filename)


class SingleAuditReportFileTests(TestCase):
    """Model tests"""

    def test_filename_generated(self):
        """
        The filename field should be generated based on the FileField filename
        """
        file = SimpleUploadedFile("this is a file.pdf", b"this is a file")

        report_id = "FAKE_REPORT_ID"
        audit = baker.make(Audit, report_id=report_id, version=0)
        sar_file = baker.make(
            SingleAuditReportFile,
            file=file,
            audit=audit,
        )

        self.assertEqual(f"{report_id}.pdf", sar_file.filename)

    def test_no_late_upload(self):
        """
        If the associated Audit isn't in progress, we should get an error.
        """
        file = SimpleUploadedFile("this is a file.pdf", b"this is a file")

        bad_statuses = [
            status[0] for status in STATUS_CHOICES if status[0] != STATUS.IN_PROGRESS
        ]

        for status_from in bad_statuses:
            report_id = f"FAKE_REPORT_ID-{status_from}"
            audit = baker.make(
                Audit, version=0, submission_status=status_from, report_id=report_id
            )
            with self.assertRaises(LateChangeError):
                baker.make(SingleAuditReportFile, audit=audit, file=file)
