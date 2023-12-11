from .home import Home
from .manage_submission import ManageSubmissionView
from .manage_submission_access import (
    ChangeAuditeeCertifyingOfficialView,
    ChangeAuditorCertifyingOfficialView,
)
from .no_robots import no_robots
from .pre_certification_review import PreCertificationReview
from .pre_dissemination_download_view import (
    PredisseminationXlsxDownloadView,
    PredisseminationPdfDownloadView,
    PredisseminationSummaryReportDownloadView,
)
from .submission_progress_view import (  # noqa
    SubmissionProgressView,
    submission_progress_check,
)
from .tribal_data_consent import TribalDataConsent
from .upload_report_view import UploadReportView
from .unlock_after_certification import UnlockAfterCertificationView
from .views import (
    AuditeeCertificationStep1View,
    AuditeeCertificationStep2View,
    AuditInfoFormView,
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
    AuditeeCertificationStep1View,
    AuditeeCertificationStep2View,
    AuditInfoFormView,
    AuditorCertificationStep1View,
    AuditorCertificationStep2View,
    CertificationView,
    ChangeAuditeeCertifyingOfficialView,
    ChangeAuditorCertifyingOfficialView,
    CrossValidationView,
    EditSubmission,
    ExcelFileHandlerView,
    Home,
    ManageSubmissionView,
    MySubmissions,
    no_robots,
    PreCertificationReview,
    PredisseminationPdfDownloadView,
    PredisseminationSummaryReportDownloadView,
    PredisseminationXlsxDownloadView,
    ReadyForCertificationView,
    SingleAuditReportFileHandlerView,
    SubmissionProgressView,
    SubmissionView,
    TribalDataConsent,
    UnlockAfterCertificationView,
    UploadReportView,
]
