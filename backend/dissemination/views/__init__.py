from dissemination.views.download import (
    PdfDownloadView,
    XlsxDownloadView,
    PublicDataDownloadView,
    OneTimeAccessDownloadView,
    SingleSummaryReportDownloadView,
    MultipleSummaryReportDownloadView,
    FindingsSummaryReportDownloadView,
)
from dissemination.views.analytics import AnalyticsView
from dissemination.views.search import Search
from dissemination.views.summary import AuditSummaryView

views_list = [
    PdfDownloadView,
    XlsxDownloadView,
    PublicDataDownloadView,
    OneTimeAccessDownloadView,
    SingleSummaryReportDownloadView,
    MultipleSummaryReportDownloadView,
    FindingsSummaryReportDownloadView,
    Search,
    AuditSummaryView,
    AnalyticsView,
]
