from api import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

schema_view = get_schema_view(
    title="Federal Audit Clearinghouse API",
    version=settings.API_VERSION,
    url="http://localhost:8000/api/",
    renderer_classes=[JSONOpenAPIRenderer],
)

urlpatterns = [
    # path("", IndexView.as_view(), name="index"),
    path("api/schema.json", schema_view),
    path("public/api/sac", views.SACViewSet.as_view({"get": "list"}), name="sac-list"),
    path(
        "public/api/sac/<str:report_id>",
        views.SACViewSet.as_view({"get": "retrieve"}),
        name="sac-detail",
    ),
    path(
        "sac/eligibility",
        views.EligibilityFormView.as_view(),
        name="eligibility",
    ),
    path(
        "sac/ueivalidation",
        views.UEIValidationFormView.as_view(),
        name="uei-validation",
    ),
    path("sac/auditee", views.AuditeeInfoView.as_view(), name="auditee-info"),
    path(
        "sac/accessandsubmission",
        views.AccessAndSubmissionView.as_view(),
        name="accessandsubmission",
    ),
    path(
        "sac/edit/<str:report_id>",
        views.SingleAuditChecklistView.as_view(),
        name="singleauditchecklist",
    ),
    path(
        "sac/edit/<str:report_id>/federal_awards",
        views.SacFederalAwardsView.as_view(),
        name="sacfederalawards",
    ),
    path(
        "submissions",
        views.SubmissionsView.as_view(),
        name="submissions",
    ),
    path(
        "access-list",
        views.AccessListView.as_view(),
        name="access-list",
    ),
    path(
        "schemas/<str:fiscal_year>/<str:type>",
        views.SchemaView.as_view(),
        name="schemas",
    ),
    path(settings.ADMIN_URL, admin.site.urls),
    path("openid/", include("djangooidc.urls")),
    # Keep last so we can use short urls for content pages like home page etc.
    path("", include("cms.urls")),
    path("report_submission/", include('report_submission.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
