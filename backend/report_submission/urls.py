from django.urls import path
from . import views


urlpatterns = [
    path("", views.ReportSubmissionRedirectView.as_view(), name="report_submission"),
    path("eligibility/", views.EligibilityFormView.as_view(), name="eligibility"),
    path("auditeeinfo/", views.AuditeeInfoFormView.as_view(), name="auditeeinfo"),
    path(
        "accessandsubmission/",
        views.AccessAndSubmissionFormView.as_view(),
        name="accessandsubmission",
    ),
    path(
        "general-information/<str:report_id>",
        views.GeneralInformationFormView.as_view(),
        name="general_information",
    ),
    path(
        "federal-awards/<str:report_id>",
        views.FederalAwardsUploadView.as_view(),
        name="federal_awards",
    ),
    path(
        "audit-findings/<str:report_id>",
        views.AuditFindingsUploadView.as_view(),
        name="audit_findings",
    ),
    path(
        "audit-findings-text/<str:report_id>",
        views.AuditFindingsTextUploadView.as_view(),
        name="audit_findings_text",
    ),
    path(
        "CAP/<str:report_id>",
        views.CAPUploadView.as_view(),
        name="CAP",
    ),
    path(
        "additional-EINs/<str:report_id>",
        views.AdditionalEINsUploadView.as_view(),
        name="additional_EINs",
    ),
    path(
        "additional-UEIs/<str:report_id>",
        views.AdditionalUEIsUploadView.as_view(),
        name="additional_UEIs",
    ),
    path(
        "secondary-auditors/<str:report_id>",
        views.SecondaryAuditorsUploadView.as_view(),
        name="secondary_auditors",
    ),
]
