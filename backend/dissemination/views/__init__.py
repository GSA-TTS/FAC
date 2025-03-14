from dissemination.views.download import (
    PdfDownloadView,
    XlsxDownloadView,
    OneTimeAccessDownloadView,
    SingleSummaryReportDownloadView,
    MultipleSummaryReportDownloadView,
)
from dissemination.views.search import AdvancedSearch, Search, AuditSearch
from dissemination.views.summary import AuditSummaryView

views_list = [
    PdfDownloadView,
    XlsxDownloadView,
    OneTimeAccessDownloadView,
    SingleSummaryReportDownloadView,
    MultipleSummaryReportDownloadView,
    AdvancedSearch,
    Search,
    AuditSearch,
    AuditSummaryView,
]
