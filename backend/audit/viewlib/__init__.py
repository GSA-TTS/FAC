from .home import Home
from .no_robots import no_robots
from .submission_progress_view import (  # noqa
    SubmissionProgressView,
    submission_progress_check,
)
from .tribal_data_consent import TribalDataConsent
from .upload_report_view import UploadReportView
from .unlock_after_certification import UnlockAfterCertificationView

# In case we want to iterate through all the views for some reason:
views = [
    Home,
    SubmissionProgressView,
    TribalDataConsent,
    UnlockAfterCertificationView,
    UploadReportView,
    no_robots,
]
