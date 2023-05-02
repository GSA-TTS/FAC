from django.urls import path
from . import views

app_name = "report_submission"

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
        views.FederalAwards.as_view(),
        name="federal_awards",
    ),
]
