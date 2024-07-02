from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from .models import SacValidationWaiver, SingleAuditChecklist
from .admin import SacValidationWaiverAdmin
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

        self.user = User.objects.create_user(username="testuser", password="12345")
        # Create a SingleAuditChecklist instance
        self.sac = baker.make(
            SingleAuditChecklist,
            submission_status=SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION,
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
        self.assertEqual(
            self.sac.submission_status, SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED
        )

    def test_save_model_auditee_certification(self):
        """Test the save_model method of the SacValidationWaiverAdmin class when the waiver is for auditee certification"""
        # Set the SAC status to AUDITOR_CERTIFIED
        self.sac.submission_status = SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED
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
        self.assertEqual(
            self.sac.submission_status, SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED
        )

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
        self.assertEqual(
            self.sac.submission_status, SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED
        )

    def test_handle_auditee_certification(self):
        """Test the handle_auditee_certification method of the SacValidationWaiverAdmin class."""

        # Set SAC status to AUDITOR_CERTIFIED
        self.sac.submission_status = SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED
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
        self.assertEqual(
            self.sac.submission_status, SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED
        )
