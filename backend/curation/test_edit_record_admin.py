from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory

from model_bakery import baker

from .admin import EditRecordAdmin
from .models import EditRecord  # update if EditRecord lives elsewhere

REPORT_ID = "2024-01-GSAFAC-0000000001"
DEFAULT_UEI = "UEIABCDE12345"
DEFAULT_EIN = "123456789"

class TestEditRecordAdmin(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = EditRecordAdmin(EditRecord, self.site)

        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="12345",  # nosec
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="12345",  # nosec
            is_staff=False,
        )

        self.factory = RequestFactory()

        self.edit_record = baker.make(
            EditRecord,
            report_id=REPORT_ID,
            uei=DEFAULT_UEI,
            ein=DEFAULT_EIN,
        )

    def _make_request(self, user, method="post"):
        request = getattr(self.factory, method)("/admin/")
        request.user = user
        self._apply_middleware(request)
        return request

    def _apply_middleware(self, request):
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

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
        request = self._make_request(self.staff_user)
        obj = baker.prepare(
            EditRecord,
            report_id = REPORT_ID,
            field_to_edit="uei",
            uei=DEFAULT_UEI,
            new_value="CNGNPY75HBU5",
        )
        form = MagicMock()
 
        self.admin.save_model(request, obj, form, change=False)
 
        obj.refresh_from_db()
        self.assertEqual(obj.field_to_edit, "uei")
        self.assertEqual(obj.uei, DEFAULT_UEI)
        self.assertEqual(obj.new_value, "CNGNPY75HBU5")
 
    def test_save_model_ein_field_saves_successfully(self):
        """save_model should store the old EIN on the record and the replacement in new_value."""
        request = self._make_request(self.staff_user)
        obj = baker.prepare(
            EditRecord,
            report_id = REPORT_ID,
            field_to_edit="ein",
            ein=DEFAULT_EIN,
            new_value="521226027",
        )
        form = MagicMock()
 
        self.admin.save_model(request, obj, form, change=False)
 
        obj.refresh_from_db()
        self.assertEqual(obj.field_to_edit, "ein")
        self.assertEqual(obj.ein, DEFAULT_EIN)
        self.assertEqual(obj.new_value, "521226027")


