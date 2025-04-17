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
        "unlock-after-certification/<str:report_id>",
        views.UnlockAfterCertificationView.as_view(),
        name="UnlockAfterCertification",
    ),
    path(
        "manage-submission/<str:report_id>",
        views.ManageSubmissionView.as_view(),
        name="ManageSubmission",
    ),
    path(
        "manage-submission/auditor-certifying-official/<str:report_id>",
        views.ChangeAuditorCertifyingOfficialView.as_view(),
        name="ChangeAuditorCertifyingOfficial",
    ),
    path(
        "manage-submission/auditee-certifying-official/<str:report_id>",
        views.ChangeAuditeeCertifyingOfficialView.as_view(),
        name="ChangeAuditeeCertifyingOfficial",
    ),
    path(
        "manage-submission/add-editor/<str:report_id>",
        views.ChangeOrAddRoleView.as_view(),
        name="ChangeOrAddRoleView",
    ),
    path(
        "manage-submission/remove-editor/<str:report_id>",
        views.RemoveEditorView.as_view(),
        name="RemoveEditorView",
    ),
    path(
        "manage-submission/remove-report/<str:report_id>",
        views.RemoveSubmissionView.as_view(),
        name="RemoveSubmissionInProgress",
    ),
    path(
        "workbook/xlsx/<str:file_type>/<str:report_id>",
        views.PredisseminationXlsxDownloadView.as_view(),
        name="PredisseminationXlsxDownload",
    ),
    path(
        "report/pdf/<str:report_id>",
        views.PredisseminationPdfDownloadView.as_view(),
        name="PredisseminationPdfDownload",
    ),
    path(
        "summary-report/xlsx/<str:report_id>",
        views.PredisseminationSummaryReportDownloadView.as_view(),
        name="PredisseminationSummaryReportDownload",
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
