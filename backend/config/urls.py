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
        "api/sac/eligibility",
        views.EligibilityFormView.as_view(),
        name="api-eligibility",
    ),
    path(
        "api/sac/ueivalidation",
        views.UEIValidationFormView.as_view(),
        name="api-uei-validation",
    ),
    path("api/sac/auditee", views.AuditeeInfoView.as_view(), name="api-auditee-info"),
    path(
        "api/sac/accessandsubmission",
        views.AccessAndSubmissionView.as_view(),
        name="api-accessandsubmission",
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
        "schemas/<str:fiscal_year>/<str:schema_type>",
        views.SchemaView.as_view(),
        name="schemas",
    ),
    path(settings.ADMIN_URL, admin.site.urls),
    path("openid/", include("djangooidc.urls")),
    path("report_submission/", include("report_submission.urls")),
    # Due to problematic interactions between the SVG use element and
    # cross-domain rules and serving assets from S3, we need to serve this
    # particular file from Django:
    path(
        "icons/sprite.svg",
        views.Sprite.as_view(),
        name="sprite",
    ),
    path("audit/", include("audit.urls")),
    # Keep last so we can use short urls for content pages like home page etc.
    path("", include("cms.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.ENABLE_DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
