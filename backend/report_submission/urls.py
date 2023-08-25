from django.urls import path
from . import views

app_name = "report_submission"

upload_page_ids = [
    "federal-awards",
    "notes-to-sefa",
    "audit-findings",
    "audit-findings-text",
    "CAP",
    "additional-eins",
    "additional-ueis",
    "secondary-auditors",
]

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
]

for page_id in upload_page_ids:
    urlpatterns.append(
        path(
            "{}/<str:report_id>".format(page_id),
            views.UploadPageView.as_view(),
            name=page_id,
        )
    )
