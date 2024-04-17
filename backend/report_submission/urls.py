from django.urls import path
from . import views

app_name = "report_submission"

page_ids = [
    {
        "page_id": "federal-awards",
        "is_required": True,
    },
    {
        "page_id": "notes-to-sefa",
        "is_required": True,
    },
    {
        "page_id": "audit-findings",
        "is_required": False,
    },
    {
        "page_id": "audit-findings-text",
        "is_required": False,
    },
    {
        "page_id": "CAP",
        "is_required": False,
    },
    {
        "page_id": "additional-eins",
        "is_required": False,
    },
    {
        "page_id": "additional-ueis",
        "is_required": False,
    },
    {
        "page_id": "secondary-auditors",
        "is_required": False,
    },
]
upload_page_ids = [page["page_id"] for page in page_ids]
removable_file_page_ids = [
    page["page_id"] for page in page_ids if not page["is_required"]
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
            f"{page_id.lower()}/<str:report_id>",
            views.UploadPageView.as_view(),
            name=page_id,
        )
    )
for page_id in removable_file_page_ids:
    urlpatterns.append(
        path(
            f"delete-{page_id.lower()}/<str:report_id>",
            views.DeleteFileView.as_view(),
            name=f"delete-{page_id}",
        )
    )
