from django.urls import path
from . import views


urlpatterns = [
    # test page
#    path("", views.Step.as_view(), name="step"),
    path("", views.ReportSubmissionRedirectView.as_view(), name="report_submission"),
    path("eligibility/", views.EligibilityFormView.as_view(), name="eligibility"),
    path("auditeeinfo/", views.AuditeeInfoFormView.as_view(), name="auditeeinfo"),
    path("accessandsubmission/", views.AccessAndSubmissionFormView.as_view(), name="accessandsubmission")
]
