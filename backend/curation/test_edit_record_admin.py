from unittest.mock import MagicMock, patch
from model_bakery import baker

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory

from .admin import EditRecordAdmin
from audit.models.constants import STATUS
from audit.models.models import SingleAuditChecklist
from .models import EditRecord
from users.models import StaffUser

REPORT_ID = "2024-01-GSAFAC-0000000001"
STAFF_EMAIL = "staff@example.com"

OLD_UEI = "0LDANDSADUE1"
NEW_UEI = "SUPERC00LUE1"

OLD_EIN = "123456789"
NEW_EIN = "987654321"

OLD_AUDITEE_NAME = "Old Auditee Name"
NEW_AUDITEE_NAME = "New Auditee Name"


class MockRequest:
    def __init__(self, user):
        self.user = user
        self.session = {}
        self._messages = FallbackStorage(self)


class TestEditRecordAdmin(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="staffuser", email=STAFF_EMAIL, password="12345", is_staff=True
        )  # nosec
        self.staff_user = baker.make(StaffUser, staff_email=STAFF_EMAIL)

        self.sac = baker.make(
            SingleAuditChecklist,
            report_id=REPORT_ID,
            general_information={
                "auditee_uei": OLD_UEI,
                "ein": OLD_EIN,
                "auditee_name": OLD_AUDITEE_NAME,
            },
            submission_status=STATUS.DISSEMINATED,
        )
        self.sac.save()

        # Create a request object
        self.factory = RequestFactory()
        self.request = self.factory.post("/admin/curation/editrecord/add/")
        self.request.user = self.user

        # Set up the Admin site and Admin class
        self.site = AdminSite()
        self.admin = EditRecordAdmin(EditRecord, self.site)

    # -------------------------------------------------------------------------
    # Configuration tests
    # -------------------------------------------------------------------------

    def test_list_display(self):
        expected = [
            "report_id",
            "field_to_edit",
            "old_value",
            "new_value",
            "editor_email",
            "edit_timestamp",
            "status",
        ]
        self.assertEqual(self.admin.list_display, expected)

    def test_list_filter(self):
        expected = [
            "report_id",
            "field_to_edit",
            "old_value",
            "new_value",
            "editor_email",
        ]
        self.assertEqual(self.admin.list_filter, expected)

    def test_search_fields(self):
        expected = (
            "report_id",
            "field_to_edit",
            "old_value",
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
        """save_model should dispatch UEI updates successfully."""

        obj = baker.prepare(
            EditRecord,
            report_id=REPORT_ID,
            field_to_edit="uei",
            old_value=OLD_UEI,
            new_value=NEW_UEI,
            editor_email=STAFF_EMAIL,
        )
        form = MagicMock()

        with patch("curation.models.validate_inputs", return_value=True), patch(
            "curation.models.update_uei"
        ) as mock_update:
            self.admin.save_model(self.request, obj, form, change=False)

        mock_update.assert_called_once_with(
            {
                "report_id": REPORT_ID,
                "email": self.user.email,
                "old_uei": OLD_UEI,
                "new_uei": NEW_UEI,
                "old_ein": None,
                "new_ein": None,
                "old_auditee_name": None,
                "new_auditee_name": None,
                "old_authorization": None,
                "new_authorization": None,
                "old_entity_type": None,
                "new_entity_type": None,
            }
        )

        obj.refresh_from_db()
        self.assertEqual(obj.status, "success")

    def test_save_model_ein_field_saves_successfully(self):
        """save_model should dispatch EIN updates successfully."""

        obj = baker.prepare(
            EditRecord,
            report_id=REPORT_ID,
            field_to_edit="ein",
            old_value=OLD_EIN,
            new_value=NEW_EIN,
            editor_email=STAFF_EMAIL,
        )
        form = MagicMock()

        with patch("curation.models.validate_inputs", return_value=True), patch(
            "curation.models.update_simple_gen_field"
        ) as mock_update:
            self.admin.save_model(self.request, obj, form, change=False)

        mock_update.assert_called_once_with(
            {
                "report_id": REPORT_ID,
                "email": self.user.email,
                "old_uei": None,
                "new_uei": None,
                "old_ein": OLD_EIN,
                "new_ein": NEW_EIN,
                "old_auditee_name": None,
                "new_auditee_name": None,
                "old_authorization": None,
                "new_authorization": None,
                "old_entity_type": None,
                "new_entity_type": None,
            },
            "ein",
        )

        obj.refresh_from_db()
        self.assertEqual(obj.status, "success")

    def test_save_model_auditee_name_field_saves_successfully(self):
        """save_model should dispatch auditee name updates successfully."""

        obj = baker.prepare(
            EditRecord,
            report_id=REPORT_ID,
            field_to_edit="auditee_name",
            old_value=OLD_AUDITEE_NAME,
            new_value=NEW_AUDITEE_NAME,
            editor_email=STAFF_EMAIL,
        )
        form = MagicMock()

        with patch("curation.models.validate_inputs", return_value=True), patch(
            "curation.models.update_simple_gen_field"
        ) as mock_update:
            self.admin.save_model(self.request, obj, form, change=False)

        mock_update.assert_called_once_with(
            {
                "report_id": REPORT_ID,
                "email": self.user.email,
                "old_uei": None,
                "new_uei": None,
                "old_ein": None,
                "new_ein": None,
                "old_auditee_name": OLD_AUDITEE_NAME,
                "new_auditee_name": NEW_AUDITEE_NAME,
                "old_authorization": None,
                "new_authorization": None,
                "old_entity_type": None,
                "new_entity_type": None,
            },
            "auditee_name",
        )

        obj.refresh_from_db()
        self.assertEqual(obj.status, "success")
