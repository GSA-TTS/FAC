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
]
