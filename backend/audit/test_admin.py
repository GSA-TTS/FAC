from unittest.mock import MagicMock, patch
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from .models import (
    Audit,
    AuditValidationWaiver,
    SacValidationWaiver,
    SingleAuditChecklist,
    History,
)
from .models.constants import STATUS, EventType
from .models.waivers import UeiValidationWaiver
from .admin import (
    AuditAdmin,
    AuditValidationWaiverAdmin,
    SacValidationWaiverAdmin,
    audit_delete_flagged_records,
    flag_audit_for_removal,
    audit_revert_to_in_progress,
)
from django.utils import timezone
from model_bakery import baker
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware


class MockRequest:
    def __init__(self, user):
        self.user = user
        self.session = {}
        self._messages = FallbackStorage(self)


class TestSacValidationWaiverAdmin(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )  # nosec
        # Create a SingleAuditChecklist instance
        self.sac = baker.make(
            SingleAuditChecklist,
            submission_status=STATUS.READY_FOR_CERTIFICATION,
        )

        # Create a request object
        self.factory = RequestFactory()
        self.request = self.factory.post("/admin/audit/sacvalidationwaiver/add/")
        self.request.user = self.user

        # Add session and message middleware to the request
        self.middleware_process(self.request)

        # Set up the Admin site and Admin class
        self.site = AdminSite()
        self.admin = SacValidationWaiverAdmin(SacValidationWaiver, self.site)

    def middleware_process(self, request):
        """Apply middleware to the request object"""
        # Create and apply session middleware
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()
        # Create and apply message middleware
        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

    def test_save_model_auditor_certification(self):
        """Test the save_model method of the SacValidationWaiverAdmin class when the waiver is for auditor certification"""
        # Create a SacValidationWaiver instance
        waiver = baker.make(
            SacValidationWaiver,
            report_id=self.sac,
            timestamp=timezone.now(),
            approver_email="approver@example.com",
            approver_name="Approver Name",
            requester_email="requester@example.com",
            requester_name="Requester Name",
            justification="Test justification",
            waiver_types=[SacValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL],
        )

        form = SacValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(self.request, waiver, form, change=False)

        # Checking results
        self.sac.refresh_from_db()
        self.assertEqual(self.sac.submission_status, STATUS.AUDITOR_CERTIFIED)

    def test_save_model_auditee_certification(self):
        """Test the save_model method of the SacValidationWaiverAdmin class when the waiver is for auditee certification"""
        # Set the SAC status to AUDITOR_CERTIFIED
        self.sac.submission_status = STATUS.AUDITOR_CERTIFIED
        self.sac.save()

        # Create a SacValidationWaiver instance
        waiver = baker.make(
            SacValidationWaiver,
            report_id=self.sac,
            timestamp=timezone.now(),
            approver_email="approver@example.com",
            approver_name="Approver Name",
            requester_email="requester@example.com",
            requester_name="Requester Name",
            justification="Test justification",
            waiver_types=[SacValidationWaiver.TYPES.AUDITEE_CERTIFYING_OFFICIAL],
        )

        form = SacValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(self.request, waiver, form, change=False)

        # Checking results
        self.sac.refresh_from_db()
        self.assertEqual(self.sac.submission_status, STATUS.AUDITEE_CERTIFIED)

    def test_save_model_invalid_status(self):
        # Set SAC status to an invalid one
        self.sac.submission_status = "INVALID_STATUS"
        self.sac.save()

        # Create a SacValidationWaiver instance
        waiver = baker.make(
            SacValidationWaiver,
            report_id=self.sac,
            timestamp=timezone.now(),
            approver_email="approver@example.com",
            approver_name="Approver Name",
            requester_email="requester@example.com",
            requester_name="Requester Name",
            justification="Test justification",
            waiver_types=[SacValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL],
        )

        form = SacValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(self.request, waiver, form, change=False)

        # Check if the expected error message was added
        messages = list(self.request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("Cannot apply waiver to SAC with status", messages[0].message)

    def test_handle_auditor_certification(self):
        """Test the handle_auditor_certification method of the SacValidation"""
        # Simulating auditor certification
        waiver = baker.make(
            SacValidationWaiver,
            report_id=self.sac,
            timestamp=timezone.now(),
            waiver_types=[SacValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL],
        )
        self.admin.handle_auditor_certification(self.request, waiver, self.sac)

        # Checking results
        self.sac.refresh_from_db()
        self.assertEqual(self.sac.submission_status, STATUS.AUDITOR_CERTIFIED)

    def test_handle_auditee_certification(self):
        """Test the handle_auditee_certification method of the SacValidationWaiverAdmin class."""

        # Set SAC status to AUDITOR_CERTIFIED
        self.sac.submission_status = STATUS.AUDITOR_CERTIFIED
        self.sac.save()

        # Simulating auditee certification
        waiver = baker.make(
            SacValidationWaiver,
            report_id=self.sac,
            timestamp=timezone.now(),
            waiver_types=[SacValidationWaiver.TYPES.AUDITEE_CERTIFYING_OFFICIAL],
        )
        self.admin.handle_auditee_certification(self.request, waiver, self.sac)

        # Checking results
        self.sac.refresh_from_db()
        self.assertEqual(self.sac.submission_status, STATUS.AUDITEE_CERTIFIED)


class TestAuditValiationWaiverAdmin(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )  # nosec
        # Create an Audit instance
        self.audit = baker.make(
            Audit,
            submission_status=STATUS.READY_FOR_CERTIFICATION,
            version=0,
        )

        # Create a request object
        self.factory = RequestFactory()
        self.request = self.factory.post("/admin/audit/auditvalidationwaiver/add/")
        self.request.user = self.user

        # Add session and message middleware to the request
        self.middleware_process(self.request)

        # Set up the Admin site and Admin class
        self.site = AdminSite()
        self.admin = AuditValidationWaiverAdmin(AuditValidationWaiver, self.site)

    def middleware_process(self, request):
        """Apply middleware to the request object"""
        # Create and apply session middleware
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()
        # Create and apply message middleware
        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

    def test_save_model_auditor_certification(self):
        """Test the save_model method of the AuditValidationWaiverAdmin class when the waiver is for auditor certification"""
        # Create a AuditValidationWaiver instance
        waiver = baker.make(
            AuditValidationWaiver,
            report_id=self.audit,
            timestamp=timezone.now(),
            approver_email="approver@example.com",
            approver_name="Approver Name",
            requester_email="requester@example.com",
            requester_name="Requester Name",
            justification="Test justification",
            waiver_types=[AuditValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL],
        )

        form = AuditValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(self.request, waiver, form, change=False)

        # Checking results
        self.audit.refresh_from_db()
        self.assertEqual(self.audit.submission_status, STATUS.AUDITOR_CERTIFIED)

    def test_save_model_auditee_certification(self):
        """Test the save_model method of the AuditValidationWaiverAdmin class when the waiver is for auditee certification"""
        # Set the audit status to AUDITOR_CERTIFIED
        self.audit.submission_status = STATUS.AUDITOR_CERTIFIED
        self.audit.save()

        # Create a AuditValidationWaiver instance
        waiver = baker.make(
            AuditValidationWaiver,
            report_id=self.audit,
            timestamp=timezone.now(),
            approver_email="approver@example.com",
            approver_name="Approver Name",
            requester_email="requester@example.com",
            requester_name="Requester Name",
            justification="Test justification",
            waiver_types=[AuditValidationWaiver.TYPES.AUDITEE_CERTIFYING_OFFICIAL],
        )

        form = AuditValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(self.request, waiver, form, change=False)

        # Checking results
        self.audit.refresh_from_db()
        self.assertEqual(self.audit.submission_status, STATUS.AUDITEE_CERTIFIED)

    def test_save_model_invalid_status(self):
        # Set audit status to an invalid one
        self.audit.submission_status = "INVALID_STATUS"
        self.audit.save()

        # Create a AuditValidationWaiver instance
        waiver = baker.make(
            AuditValidationWaiver,
            report_id=self.audit,
            timestamp=timezone.now(),
            approver_email="approver@example.com",
            approver_name="Approver Name",
            requester_email="requester@example.com",
            requester_name="Requester Name",
            justification="Test justification",
            waiver_types=[AuditValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL],
        )

        form = AuditValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(self.request, waiver, form, change=False)

        # Check if the expected error message was added
        messages = list(self.request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("Cannot apply waiver to Audit with status", messages[0].message)

    def test_handle_auditor_certification(self):
        """Test the handle_auditor_certification method of the AuditValidation"""
        # Simulating auditor certification
        waiver = baker.make(
            AuditValidationWaiver,
            report_id=self.audit,
            timestamp=timezone.now(),
            waiver_types=[AuditValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL],
        )
        self.admin.handle_auditor_certification(self.request, waiver, self.audit)

        # Checking results
        self.audit.refresh_from_db()
        self.assertEqual(self.audit.submission_status, STATUS.AUDITOR_CERTIFIED)

    def test_handle_auditee_certification(self):
        """Test the handle_auditee_certification method of the AuditValidationWaiverAdmin class."""

        # Set audit status to AUDITOR_CERTIFIED
        self.audit.submission_status = STATUS.AUDITOR_CERTIFIED
        self.audit.save()

        # Simulating auditee certification
        waiver = baker.make(
            AuditValidationWaiver,
            report_id=self.audit,
            timestamp=timezone.now(),
            waiver_types=[AuditValidationWaiver.TYPES.AUDITEE_CERTIFYING_OFFICIAL],
        )
        self.admin.handle_auditee_certification(self.request, waiver, self.audit)

        # Checking results
        self.audit.refresh_from_db()
        self.assertEqual(self.audit.submission_status, STATUS.AUDITEE_CERTIFIED)


class TestAdminActions(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = AuditAdmin(Audit, self.site)
        self.request = RequestFactory().get("/admin/audit/audit/")
        self.request.user = baker.make(User, is_staff=True)
        self.request.session = {}
        self.request._messages = FallbackStorage(self.request)

        # Sample records
        self.report1 = baker.make(
            Audit,
            report_id="RPT001",
            submission_status=STATUS.FLAGGED_FOR_REMOVAL,
            version=0,
        )
        self.report2 = baker.make(
            Audit,
            report_id="RPT002",
            submission_status=STATUS.IN_PROGRESS,
            version=0,
        )

    def test_revert_to_in_progress_success(self):
        """
        When reverting to in progress, a report that is flagged_for_removal should become in_progress.
        """
        queryset = Audit.objects.filter(report_id="RPT001")
        audit_revert_to_in_progress(self.admin, self.request, queryset)

        self.report1.refresh_from_db()
        self.assertEqual(self.report1.submission_status, STATUS.IN_PROGRESS)
        messages = [m.message for m in self.request._messages]
        self.assertIn(
            "Successfully reverted report(s) (RPT001) back to In Progress.", messages
        )

    def test_revert_to_in_progress_failure(self):
        """
        When reverting to in progress, a report that is already in_progress should stay that way.
        """
        queryset = Audit.objects.filter(report_id="RPT002")
        audit_revert_to_in_progress(self.admin, self.request, queryset)

        self.report2.refresh_from_db()
        self.assertEqual(self.report2.submission_status, STATUS.IN_PROGRESS)
        messages = [m.message for m in self.request._messages]
        self.assertIn("Report RPT002 is not flagged for removal.", messages)

    def test_flag_for_removal_success(self):
        """
        When flagging a report for removal, a report that is in_progress should become flagged_for_removal.
        """
        queryset = Audit.objects.filter(report_id="RPT002")
        flag_audit_for_removal(self.admin, self.request, queryset)

        self.report2.refresh_from_db()
        self.assertEqual(self.report2.submission_status, STATUS.FLAGGED_FOR_REMOVAL)
        messages = [m.message for m in self.request._messages]
        self.assertIn("Successfully flagged report(s) (RPT002) for removal.", messages)

    def test_flag_for_removal_already_flagged(self):
        """
        When flagging a report for removal, a report that is already flagged should stay that way.
        """
        queryset = Audit.objects.filter(report_id="RPT001")
        flag_audit_for_removal(self.admin, self.request, queryset)

        self.report1.refresh_from_db()
        self.assertEqual(self.report1.submission_status, STATUS.FLAGGED_FOR_REMOVAL)
        messages = [m.message for m in self.request._messages]
        self.assertIn("Report(s) (RPT001) were already flagged.", messages)


class TestDeleteFlaggedRecordsAdminAction(TestCase):

    @patch("audit.admin.audit_remove_workbook_artifacts")
    @patch("audit.admin.audit_remove_singleauditreport_pdf")
    def test_delete_flagged_records_success(
        self,
        mock_audit_remove_workbook_artifacts,
        mock_audit_remove_singleauditreport_pd,
    ):
        AUDITEE_UEI = "ABCDHJH74DW7"
        REPORT_ID = "1900-01-GSAFAC-0000000001"
        UPDATED_AT = "2023-03-01"

        audit = baker.make(
            Audit,
            report_id=REPORT_ID,
            submission_status=STATUS.FLAGGED_FOR_REMOVAL,
            audit={"general_information": {"auditee_uei": AUDITEE_UEI}},
            version=0,
            updated_at=UPDATED_AT,
        )
        baker.make(
            History,
            event=EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
            report_id=REPORT_ID,
            version=audit.version,
            updated_at=UPDATED_AT,
            updated_by=audit.created_by,
            event_data=audit.audit,
        )
        baker.make(UeiValidationWaiver, uei=AUDITEE_UEI)
        baker.make(AuditValidationWaiver, report_id=audit)

        modeladmin = MagicMock()
        queryset = Audit.objects.filter(id=audit.id)

        audit_delete_flagged_records(modeladmin, None, queryset)

        # Assert that related objects and audit are deleted
        self.assertFalse(Audit.objects.filter(report_id=REPORT_ID).exists())
        self.assertFalse(UeiValidationWaiver.objects.filter(uei=AUDITEE_UEI).exists())
        self.assertFalse(
            AuditValidationWaiver.objects.filter(report_id=REPORT_ID).exists()
        )
        mock_audit_remove_singleauditreport_pd.assert_called_once()
        mock_audit_remove_workbook_artifacts.assert_called_once()

    @patch("audit.admin.remove_workbook_artifacts")
    @patch("audit.admin.remove_singleauditreport_pdf")
    def test_delete_flagged_records_skips_non_flagged(
        self, mock_remove_workbook_artifacts, mock_remove_singleauditreport_pd
    ):
        REPORT_ID = "1900-01-GSAFAC-0000000002"
        AUDITEE_UEI = "EFJHHJH74DW7"

        sac = baker.make(
            Audit,
            report_id=REPORT_ID,
            submission_status="in_progress",
            audit={"general_information": {"auditee_uei": AUDITEE_UEI}},
            version=0,
        )

        modeladmin = MagicMock()
        queryset = Audit.objects.filter(id=sac.id)

        audit_delete_flagged_records(modeladmin, None, queryset)

        # Assert that SAC is not deleted
        self.assertTrue(Audit.objects.filter(report_id=REPORT_ID).exists())
        mock_remove_workbook_artifacts.assert_not_called()
        mock_remove_singleauditreport_pd.assert_not_called()
