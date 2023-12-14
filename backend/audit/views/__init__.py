from .home import Home
from .manage_submission import ManageSubmissionView
from .manage_submission_access import (
    ChangeOrAddRoleView,
    ChangeAuditeeCertifyingOfficialView,
    ChangeAuditorCertifyingOfficialView,
)
from .no_robots import no_robots
from .submission_progress_view import (  # noqa
    SubmissionProgressView,
    submission_progress_check,
)
from .tribal_data_consent import TribalDataConsent
from .upload_report_view import UploadReportView
from .unlock_after_certification import UnlockAfterCertificationView
from .views import (
    AuditInfoFormView,
    AuditeeCertificationStep1View,
    AuditeeCertificationStep2View,
    AuditorCertificationStep1View,
    AuditorCertificationStep2View,
    CertificationView,
    CrossValidationView,
    EditSubmission,
    ExcelFileHandlerView,
    MySubmissions,
    ReadyForCertificationView,
    SingleAuditReportFileHandlerView,
    SubmissionView,
)

# In case we want to iterate through all the views for some reason:
views = [
    AuditInfoFormView,
    AuditeeCertificationStep1View,
    AuditeeCertificationStep2View,
    AuditorCertificationStep1View,
    AuditorCertificationStep2View,
    CertificationView,
    ChangeOrAddRoleView,
    ChangeAuditeeCertifyingOfficialView,
    ChangeAuditorCertifyingOfficialView,
    CrossValidationView,
    EditSubmission,
    ExcelFileHandlerView,
    Home,
    MySubmissions,
    ManageSubmissionView,
    ReadyForCertificationView,
    SingleAuditReportFileHandlerView,
    SubmissionProgressView,
    SubmissionView,
    TribalDataConsent,
    UnlockAfterCertificationView,
    UploadReportView,
    no_robots,
]
