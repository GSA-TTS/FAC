from django.urls import path

from audit.fixtures.excel import FORM_SECTIONS
from audit import views

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
        views.AuditorCertificationStep1View.as_view(),
        name="AuditorCertification",
    ),
    path(
        "auditor-certification-confirm/<str:report_id>",
        views.AuditorCertificationStep2View.as_view(),
        name="AuditorCertificationConfirm",
    ),
    path(
        "auditee-certification/<str:report_id>",
        views.AuditeeCertificationStep1View.as_view(),
        name="AuditeeCertification",
    ),
    path(
        "auditee-certification-confirm/<str:report_id>",
        views.AuditeeCertificationStep2View.as_view(),
        name="AuditeeCertificationConfirm",
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
    path(
        "tribal-data-release/<str:report_id>",
        views.TribalDataConsent.as_view(),
        name="TribalAuditConsent",
    ),
    path(
        "cross-validation/<str:report_id>",
        views.CrossValidationView.as_view(),
        name="CrossValidation",
    ),
    path(
        "search/",
        views.AuditSearchView.as_view(),
        name="AuditSearch",
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
