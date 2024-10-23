import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone
from model_bakery import baker
from django.test import RequestFactory
from unittest.mock import patch
from audit.models import (
    SacValidationWaiver,
    SingleAuditChecklist,
    Access,
    DeletedAccess,
    ExcelFile,
    SingleAuditReportFile,
    SubmissionEvent,
    UeiValidationWaiver,
)
from audit.admin import (
    SacValidationWaiverAdmin,
    SACAdmin,
    AccessAdmin,
    DeletedAccessAdmin,
    ExcelFileAdmin,
    AuditReportAdmin,
    SubmissionEventAdmin,
    UeiValidationWaiverAdmin,
)


# Fixtures for users
@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="adminuser", password="12345", email="admin@example.com"
    )

@pytest.fixture
def normal_user(db):
    return User.objects.create_user(username="testuser", password="12345")

# Fixture for RequestFactory
@pytest.fixture
def rf():
    return RequestFactory()

# Middleware application function
def mock_middleware_process(request):
    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()
    message_middleware = MessageMiddleware(lambda req: None)
    message_middleware.process_request(request)

# Mock requests with admin and normal users
@pytest.fixture
def mock_request_factory_admin(rf, admin_user):
    request = rf.get("/")
    request.user = admin_user
    mock_middleware_process(request)
    return request

@pytest.fixture
def mock_request_factory_normal(rf, normal_user):
    request = rf.get("/")
    request.user = normal_user
    mock_middleware_process(request)
    return request

# Fixtures for models
@pytest.fixture
def sac(db):
    return baker.make(
        SingleAuditChecklist,
        submission_status=SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION,
    )

@pytest.fixture
def waiver(sac):
    return baker.make(
        SacValidationWaiver,
        report_id=sac,
        approver_email="approver@example.com",
        approver_name="Approver Name",
        requester_email="requester@example.com",
        requester_name="Requester Name",
        justification="Justification for waiver.",
        waiver_types=[SacValidationWaiver.TYPES.AUDITOR_CERTIFYING_OFFICIAL],
        timestamp=timezone.now(),
    )

@pytest.fixture
def access(sac):
    return baker.make(
        Access,
        sac=sac,
        role="editor",
        email="test@example.com",
        user=baker.make(User),
    )

@pytest.fixture
def deleted_access(sac):
    return baker.make(
        DeletedAccess,
        sac=sac,
        role="editor",
        email="deleted@example.com",
        removed_by_email="remover@example.com",
    )

@pytest.fixture
def excel_file(sac):
    return baker.make(
        ExcelFile,
        filename="test.xlsx",
        user=baker.make(User),
        date_created=timezone.now(),
    )

@pytest.fixture
def report_file(sac):
    return baker.make(
        SingleAuditReportFile,
        filename="report.pdf",
        user=baker.make(User),
        date_created=timezone.now(),
        component_page_numbers="1,2,3",
    )

@pytest.fixture
def submission_event(sac):
    return baker.make(
        SubmissionEvent,
        sac=sac,
        user=baker.make(User),
        event=SubmissionEvent.EventType.SUBMISSION,
        timestamp=timezone.now(),
    )

@pytest.fixture
def uei_waiver():
    return baker.make(
        UeiValidationWaiver,
        uei="123456789",
        approver_email="approver@example.com",
        requester_email="requester@example.com",
        justification="Valid reason",
        timestamp=timezone.now(),
    )

# Test classes for each admin class
@pytest.mark.django_db
class TestSACAdmin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = SACAdmin(SingleAuditChecklist, self.site)

    def test_has_permission(self, mock_request_factory_admin):
        request = mock_request_factory_admin
        assert self.admin.has_module_permission(request) is True
        assert self.admin.has_view_permission(request) is True

    def test_has_no_permission(self, mock_request_factory_normal):
        request = mock_request_factory_normal
        assert self.admin.has_module_permission(request) is False
        assert self.admin.has_view_permission(request) is False

    def test_list_display(self):
        assert self.admin.list_display == (
            "id",
            "report_id",
            "cognizant_agency",
            "oversight_agency",
        )

    def test_list_filter(self):
        assert self.admin.list_filter == [
            "cognizant_agency",
            "oversight_agency",
            "oversight_agency",
            "submission_status",
        ]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ("submitted_by",)

    def test_search_fields(self):
        assert self.admin.search_fields == (
            "general_information__auditee_uei",
            "report_id",
        )

@pytest.mark.django_db
class TestAccessAdmin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = AccessAdmin(Access, self.site)

    def test_has_permission(self, mock_request_factory_admin):
        request = mock_request_factory_admin
        assert self.admin.has_module_permission(request) is True
        assert self.admin.has_view_permission(request) is True

    def test_has_no_permission(self, mock_request_factory_normal):
        request = mock_request_factory_normal
        assert self.admin.has_module_permission(request) is False
        assert self.admin.has_view_permission(request) is False

    def test_list_display(self):
        assert self.admin.list_display == ("sac", "role", "email")

    def test_list_filter(self):
        assert self.admin.list_filter == ["role"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ("sac", "user")

    def test_search_fields(self):
        assert self.admin.search_fields == ("email", "sac__report_id")

@pytest.mark.django_db
class TestDeletedAccessAdmin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = DeletedAccessAdmin(DeletedAccess, self.site)

    def test_has_permission(self, mock_request_factory_admin):
        request = mock_request_factory_admin
        assert self.admin.has_module_permission(request) is True
        assert self.admin.has_view_permission(request) is True

    def test_has_no_permission(self, mock_request_factory_normal):
        request = mock_request_factory_normal
        assert self.admin.has_module_permission(request) is False
        assert self.admin.has_view_permission(request) is False

    def test_list_display(self):
        assert self.admin.list_display == ("sac", "role", "email")

    def test_list_filter(self):
        assert self.admin.list_filter == ["role"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ("sac",)

    def test_search_fields(self):
        assert self.admin.search_fields == (
            "email",
            "removed_by_email",
            "sac__report_id",
        )

@pytest.mark.django_db
class TestExcelFileAdmin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = ExcelFileAdmin(ExcelFile, self.site)

    def test_list_display(self):
        assert self.admin.list_display == ("filename", "user", "date_created")

    # Since ExcelFileAdmin doesn't have custom methods, coverage is already sufficient

@pytest.mark.django_db
class TestAuditReportAdmin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = AuditReportAdmin(SingleAuditReportFile, self.site)

    def test_list_display(self):
        assert self.admin.list_display == (
            "filename",
            "user",
            "date_created",
            "component_page_numbers",
        )

    # Since AuditReportAdmin doesn't have custom methods, coverage is already sufficient

@pytest.mark.django_db
class TestSubmissionEventAdmin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = SubmissionEventAdmin(SubmissionEvent, self.site)

    def test_list_display(self):
        assert self.admin.list_display == ("sac", "user", "timestamp", "event")

    def test_search_fields(self):
        assert self.admin.search_fields == ("sac__report_id", "user__username")

    # Since SubmissionEventAdmin doesn't have custom methods, coverage is already sufficient

@pytest.mark.django_db
class TestUeiValidationWaiverAdmin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = UeiValidationWaiverAdmin(UeiValidationWaiver, self.site)

    def test_has_permission(self, mock_request_factory_admin):
        request = mock_request_factory_admin
        assert self.admin.has_add_permission(request) is True
        assert self.admin.has_change_permission(request) is True
        assert self.admin.has_delete_permission(request) is True
        assert self.admin.has_view_permission(request) is True

    def test_has_no_permission(self, mock_request_factory_normal):
        request = mock_request_factory_normal
        assert self.admin.has_add_permission(request) is False
        assert self.admin.has_change_permission(request) is False
        assert self.admin.has_delete_permission(request) is False
        assert self.admin.has_view_permission(request) is False

    def test_list_display(self):
        assert self.admin.list_display == (
            "id",
            "uei",
            "timestamp",
            "expiration",
            "approver_email",
            "requester_email",
            "justification",
        )

    def test_search_fields(self):
        assert self.admin.search_fields == (
            "id",
            "uei",
            "approver_email",
            "requester_email",
        )

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ("timestamp",)

    def test_save_model(self, mock_request_factory_admin, uei_waiver):
        request = mock_request_factory_admin
        form = UeiValidationWaiverAdmin.form(instance=uei_waiver)
        self.admin.save_model(request, uei_waiver, form, change=False)
        # No exception means success; check logs or any side effects if necessary

@pytest.mark.django_db
class TestSacValidationWaiverAdmin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = SacValidationWaiverAdmin(SacValidationWaiver, self.site)

    def test_has_permission(self, mock_request_factory_admin):
        request = mock_request_factory_admin
        assert self.admin.has_add_permission(request) is True
        assert self.admin.has_change_permission(request) is True
        assert self.admin.has_delete_permission(request) is True
        assert self.admin.has_view_permission(request) is True

    def test_has_no_permission(self, mock_request_factory_normal):
        request = mock_request_factory_normal
        assert self.admin.has_add_permission(request) is False
        assert self.admin.has_change_permission(request) is False
        assert self.admin.has_delete_permission(request) is False
        assert self.admin.has_view_permission(request) is False

    def test_save_model_auditor_certification(
        self, mock_request_factory_admin, sac, waiver
    ):
        request = mock_request_factory_admin
        form = SacValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(request, waiver, form, change=False)
        sac.refresh_from_db()
        assert sac.submission_status == SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED

    def test_save_model_auditee_certification(
        self, mock_request_factory_admin, sac, waiver
    ):
        request = mock_request_factory_admin
        sac.submission_status = SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED
        sac.save()
        waiver.waiver_types = [
            SacValidationWaiver.TYPES.AUDITEE_CERTIFYING_OFFICIAL
        ]
        waiver.save()
        form = SacValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(request, waiver, form, change=False)
        sac.refresh_from_db()
        assert sac.submission_status == SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED

    def test_save_model_invalid_status(
        self, mock_request_factory_admin, sac, waiver
    ):
        request = mock_request_factory_admin
        sac.submission_status = "INVALID_STATUS"
        sac.save()
        form = SacValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(request, waiver, form, change=False)
        messages = list(request._messages)
        assert len(messages) == 1
        assert "Cannot apply waiver to SAC with status" in messages[0].message

    def test_save_model_exception(
        self, mock_request_factory_admin, waiver
    ):
        request = mock_request_factory_admin
        waiver.report_id = None  # This will cause an exception
        form = SacValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(request, waiver, form, change=False)
        messages = list(request._messages)
        assert len(messages) == 1
        assert "Error saving SAC waiver" in messages[0].message

    def test_handle_auditor_certification(
        self, mock_request_factory_admin, sac, waiver
    ):
        request = mock_request_factory_admin
        self.admin.handle_auditor_certification(request, waiver, sac)
        sac.refresh_from_db()
        assert sac.submission_status == SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED
        assert sac.auditor_certification is not None

    def test_handle_auditee_certification(
        self, mock_request_factory_admin, sac, waiver
    ):
        request = mock_request_factory_admin
        sac.submission_status = SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED
        sac.save()
        waiver.waiver_types = [
            SacValidationWaiver.TYPES.AUDITEE_CERTIFYING_OFFICIAL
        ]
        waiver.save()
        self.admin.handle_auditee_certification(request, waiver, sac)
        sac.refresh_from_db()
        assert sac.submission_status == SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED
        assert sac.auditee_certification is not None

    def test_handle_duplicate_finding_waiver(
        self, mock_request_factory_admin, sac, waiver
    ):
        request = mock_request_factory_admin
        sac.submission_status = SingleAuditChecklist.STATUS.IN_PROGRESS
        sac.save()
        waiver.waiver_types = [
            SacValidationWaiver.TYPES.FINDING_REFERENCE_NUMBER
        ]
        waiver.save()
        form = SacValidationWaiverAdmin.form(instance=waiver)
        self.admin.save_model(request, waiver, form, change=False)
        sac.refresh_from_db()
        # Since the status remains IN_PROGRESS, check if waiver was applied
        # No exception and successful save indicates the waiver was handled

    def test_handle_invalid_waiver_type(
        self, mock_request_factory_admin, sac, waiver
    ):
        request = mock_request_factory_admin
        waiver.waiver_types = ["INVALID_WAIVER_TYPE"]
        waiver.save()
        form = SacValidationWaiverAdmin.form(instance=waiver)
        with pytest.raises(Exception):
            self.admin.save_model(request, waiver, form, change=False)

