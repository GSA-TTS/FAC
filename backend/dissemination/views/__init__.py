from dissemination.views.download import (
    PdfDownloadView,
    XlsxDownloadView,
    PublicDataDownloadView,
    OneTimeAccessDownloadView,
    SingleSummaryReportDownloadView,
    MultipleSummaryReportDownloadView,
)
from dissemination.views.search import AuditSearch
from dissemination.views.summary import AuditSummaryView

views_list = [
    PdfDownloadView,
    XlsxDownloadView,
    PublicDataDownloadView,
    OneTimeAccessDownloadView,
    SingleSummaryReportDownloadView,
    MultipleSummaryReportDownloadView,
    AuditSearch,
    AuditSummaryView,
]
