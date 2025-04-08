from .audit_info_form_view import AuditInfoFormView
from .auditee_certification import (
    AuditeeCertificationStep1View,
    AuditeeCertificationStep2View,
)
from .auditor_certification import (
    AuditorCertificationStep1View,
    AuditorCertificationStep2View,
)
from .certification import CertificationView, ReadyForCertificationView
from .cross_validation import CrossValidationView
from .excel_file_handler import ExcelFileHandlerView
from .home import Home
from .home import Maintenance
from .manage_submission import ManageSubmissionView
from .manage_submission_access import (
    ChangeOrAddRoleView,
    ChangeAuditeeCertifyingOfficialView,
    ChangeAuditorCertifyingOfficialView,
    RemoveEditorView,
)
from .no_robots import no_robots
from .pre_dissemination_download_view import (
    PredisseminationXlsxDownloadView,
    PredisseminationPdfDownloadView,
    PredisseminationSummaryReportDownloadView,
)
from .remove_submission_in_progress import RemoveSubmissionView
from .single_audit_report_file_handler import SingleAuditReportFileHandlerView
from .submission_progress_view import (  # noqa
    SubmissionProgressView,
    submission_progress_check,
)
from .submissions import EditSubmission, MySubmissions, SubmissionView
from .tribal_data_consent import TribalDataConsent
from .upload_report_view import UploadReportView
from .unlock_after_certification import UnlockAfterCertificationView

# In case we want to iterate through all the views for some reason:
views_list = [
    AuditInfoFormView,
    AuditeeCertificationStep1View,
    AuditeeCertificationStep2View,
    AuditInfoFormView,
    AuditorCertificationStep1View,
    AuditorCertificationStep2View,
    CertificationView,
    ChangeOrAddRoleView,
    ChangeAuditeeCertifyingOfficialView,
    ChangeAuditorCertifyingOfficialView,
    RemoveEditorView,
    CrossValidationView,
    EditSubmission,
    ExcelFileHandlerView,
    Home,
    Maintenance,
    ManageSubmissionView,
    MySubmissions,
    no_robots,
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
    RemoveSubmissionView,
]
