from django.urls import path

from .fixtures.excel import CORRECTIVE_ACTION_PLAN, FEDERAL_AWARDS_EXPENDED, FINDINGS_TEXT, FINDINGS_UNIFORM_GUIDANCE
from . import views

app_name = "audit"
form_sections = [CORRECTIVE_ACTION_PLAN, FEDERAL_AWARDS_EXPENDED, FINDINGS_TEXT, FINDINGS_UNIFORM_GUIDANCE]
urlpatterns = [
    path("", views.MySubmissions.as_view(), name="MySubmissions"),
    path("<str:report_id>", views.EditSubmission.as_view(), name="EditSubmission"),

]

for form_section in form_sections:
    urlpatterns.append(
        path(
            f"excel/{form_section}/<str:report_id>",
            views.ExcelFileHandlerView.as_view(),
            name=form_section,
            kwargs={"form_section": form_section},
        )
    )
