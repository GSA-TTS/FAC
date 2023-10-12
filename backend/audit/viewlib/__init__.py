from .submission_progress_view import (  # noqa
    SubmissionProgressView,
    submission_progress_check,
)
from .tribal_data_consent import TribalDataConsent

from .upload_report_view import UploadReportView

# In case we want to iterate through all the views for some reason:
views = [SubmissionProgressView, UploadReportView, TribalDataConsent]
