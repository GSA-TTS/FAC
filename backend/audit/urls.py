from django.urls import path

from .fixtures.excel import FORM_SECTIONS
from . import views

app_name = "audit"


def camel_to_hyphen(raw: str) -> str:
    """Convert camel case to hyphen-delimited."""
    text = f"{raw[0].lower()}{raw[1:]}"
    return "".join(c if c.islower() else f"-{c.lower()}" for c in text)


urlpatterns = [
    path("", views.MySubmissions.as_view(), name="MySubmissions"),
    path("<str:report_id>", views.EditSubmission.as_view(), name="EditSubmission"),
    path(
        "single-audit-report/<str:report_id>",
        views.SingleAuditReportFileHandlerView.as_view(),
        name="SingleAuditReport",
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
    path(
        "submission-progress/<str:report_id>",
        views.SubmissionProgressView.as_view(),
        name="SubmissionProgress",
    ),
    path(
        "audit-info/<str:report_id>",
        views.AuditInfoFormView.as_view(),
        name="AuditInfoForm",
    ),
    path(
        "upload-report/<str:report_id>",
        views.UploadReportView.as_view(),
        name="UploadReport",
    ),
]

for form_section in FORM_SECTIONS:
    urlpatterns.append(
        path(
            f"excel/{camel_to_hyphen(form_section)}/<str:report_id>",
            views.ExcelFileHandlerView.as_view(),
            name=form_section,
            kwargs={"form_section": form_section},
        )
    )
