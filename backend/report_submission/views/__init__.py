from report_submission.views.file_views import DeleteFileView, UploadPageView
from report_submission.views.general_information_form_view import (
    GeneralInformationFormView,
)
from report_submission.views.submission_views import (
    AccessAndSubmissionFormView,
    AuditeeInfoFormView,
    EligibilityFormView,
    ReportSubmissionRedirectView,
)

views_list = [
    UploadPageView,
    DeleteFileView,
    GeneralInformationFormView,
    ReportSubmissionRedirectView,
    EligibilityFormView,
    AuditeeInfoFormView,
    AccessAndSubmissionFormView,
]
