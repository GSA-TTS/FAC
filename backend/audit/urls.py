from django.urls import path
from . import views

app_name = "audit"

urlpatterns = [
    path("", views.MySubmissions.as_view(), name="MySubmissions"),
    path("<str:report_id>", views.EditSubmission.as_view(), name="EditSubmission"),
    path(
        "excel/<str:report_id>",
        views.FederalAwardsExcelFileView.as_view(),
        name="FederalAwardsExcelFile",
    ),
    path(
        "ready-for-certification/<str:report_id>",
        views.ReadyForCertificationView.as_view(),
        name="ReadyForCertification",
    ),
    path(
        "auditor-certification/<str:report_id>",
        views.AuditorCertificationView.as_view(),
        name="AuditorCertification",
    ),
    path(
        "auditee-certification/<str:report_id>",
        views.AuditeeCertificationView.as_view(),
        name="AuditeeCertification",
    ),
    path(
        "certification/<str:report_id>",
        views.CertificationView.as_view(),
        name="Certification",
    ),
    path(
        "submission/<str:report_id>",
        views.SubmissionView.as_view(),
        name="Submission",
    ),
]
