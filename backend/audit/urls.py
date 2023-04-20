from django.urls import path
from . import views

app_name = "audit"

urlpatterns = [
    path("", views.MySubmissions.as_view(), name="MySubmissions"),
    path("<str:report_id>", views.EditSubmission.as_view(), name="EditSubmission"),
    path(
        "excel/<str:form_section>/<str:report_id>",
        views.ExcelFileHandlerView.as_view(),
        name="ExcelFileHandler",
    ),

]
