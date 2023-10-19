from django.urls import path

from dissemination import views

app_name = "dissemination"

urlpatterns = [
    path("pdf/<str:report_id>", views.PdfDownloadView.as_view(), name="PdfDownload"),
    path("search/", views.Search.as_view(), name="Search"),
    path("summary/<str:report_id>", views.AuditSummaryView.as_view(), name="Summary"),
]
