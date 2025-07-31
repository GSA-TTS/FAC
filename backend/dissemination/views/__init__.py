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
from dissemination.views.search import AdvancedSearch, Search, AuditSearch
from dissemination.views.summary import AuditSummaryView

views_list = [
    PdfDownloadView,
    XlsxDownloadView,
    PublicDataDownloadView,
    OneTimeAccessDownloadView,
    SingleSummaryReportDownloadView,
    MultipleSummaryReportDownloadView,
    FindingsSummaryReportDownloadView,
    AdvancedSearch,
    Search,
    AuditSearch,
    AuditSummaryView,
    AnalyticsView,
]
