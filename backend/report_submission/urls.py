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
]
