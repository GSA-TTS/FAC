from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory

from model_bakery import baker

from backend.audit.models.constants import STATUS
from backend.audit.models.models import SingleAuditChecklist
from backend.audit.models.audit import Audit

from .admin import EditRecordAdmin
from .models import EditRecord 
from django.contrib.messages.storage.fallback import FallbackStorage

REPORT_ID = "2024-01-GSAFAC-0000000001"

OLD_UEI = "UEIABCDE12345"
NEW_UEI = "UEIABCDE67890"

OLD_EIN = "123456789"
NEW_EIN = "987654321"

class MockRequest:
    def __init__(self, user):
        self.user = user
        self.session = {}
        self._messages = FallbackStorage(self)


class TestEditRecordAdmin(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="staffuser", 
            email="staff@example.com", 
            password="12345", 
            is_staff=True
        )

        self.audit = baker.make(Audit, 
                                report_id=REPORT_ID, 
                                auditee_uei = OLD_UEI, 
                                auditee_ein=OLD_EIN, 
                                version=0)
        self.sac = baker.make(
            SingleAuditChecklist,
            report_id=self.audit.report_id,
            submission_status=STATUS.DISSEMINATED,
        )
        self.sac.save()

        # Create a request object
        self.factory = RequestFactory()
        self.request = self.factory.post("/admin/curation/editrecord/add/")
        self.request.user = self.user

        # # Add session and message middleware to the request
        self.middleware_process(self.request)
        
        # Set up the Admin site and Admin class
        self.site = AdminSite()
        self.admin = EditRecordAdmin(EditRecord, self.site)



    def middleware_process(self, request):
        """Apply middleware to the request object"""
        # Create and apply session middleware
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()
        # Create and apply message middleware
        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)


    # -------------------------------------------------------------------------
    # Configuration tests
    # -------------------------------------------------------------------------

    def test_list_display(self):
        expected = [
            "report_id",
            "uei",
            "ein",
            "field_to_edit",
            "new_value",
            "editor_email",
            "edit_timestamp",
            "status",
        ]
        self.assertEqual(self.admin.list_display, expected)

    def test_list_filter(self):
        expected = [
            "report_id",
            "uei",
            "ein",
            "field_to_edit",
            "new_value",
            "editor_email",
        ]
        self.assertEqual(self.admin.list_filter, expected)

    def test_search_fields(self):
        expected = (
            "report_id",
            "field_to_edit",
            "uei",
            "ein",
            "new_value",
            "editor_email",
        )
        self.assertEqual(self.admin.search_fields, expected)

    def test_readonly_fields(self):
        expected = ["editor_email", "edit_timestamp", "status"]
        self.assertEqual(self.admin.readonly_fields, expected)

    def test_date_hierarchy(self):
        self.assertEqual(self.admin.date_hierarchy, "edit_timestamp")

    def test_ordering(self):
        self.assertEqual(self.admin.ordering, ["edit_timestamp"])

    # -------------------------------------------------------------------------
    # save_model tests
    # -------------------------------------------------------------------------

    def test_save_model_uei_field_saves_successfully(self):
        """save_model should store the old UEI on the record and the replacement in new_value."""
        self.assertEqual(self.audit.auditee_uei, OLD_UEI)

        obj = baker.make(
            EditRecord,
            report_id = REPORT_ID,
            field_to_edit="uei",
            uei=OLD_UEI,
            new_value=NEW_UEI
        )
        form = MagicMock()
 
        self.admin.save_model(self.request, obj, form, change=False)
 
        self.sac.refresh_from_db()

        obj.refresh_from_db()

        # Get the SF_SAC from the db and assert the new uei is updated
        self.assertEqual(self.audit.auditee_uei, NEW_UEI)

        self.assertEqual(obj.field_to_edit, "uei")
        self.assertEqual(obj.uei, OLD_UEI)
        self.assertEqual(obj.new_value, NEW_UEI)
 
    def test_save_model_ein_field_saves_successfully(self):
        """save_model should store the old EIN on the record and the replacement in new_value."""
        request = self._make_request(self.user)
        obj = baker.prepare(
            EditRecord,
            report_id = REPORT_ID,
            field_to_edit="ein",
            ein=DEFAULT_EIN,
            new_value=NEW_EIN,
        )
        form = MagicMock()
 
        self.admin.save_model(request, obj, form, change=False)
 
        obj.refresh_from_db()
        self.assertEqual(obj.field_to_edit, "ein")
        self.assertEqual(obj.ein, OLD_EIN)
        self.assertEqual(obj.new_value, NEW_EIN)


