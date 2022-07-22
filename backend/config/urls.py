from api import views
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

from users.views import AuthToken

#  DRF API views
api_router = routers.DefaultRouter()
api_router.register(r"sf-sac", views.SACViewSet)

schema_view = get_schema_view(
    title="Federal Audit Clearinghouse API",
    version=settings.API_VERSION,
    url="http://localhost:8000/api/",
    renderer_classes=[JSONOpenAPIRenderer],
)

urlpatterns = [
    path("api/auth/token", AuthToken.as_view(), name="token"),
    path("api/schema.json", schema_view),
    path("api/", include(api_router.urls)),
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
    path(settings.ADMIN_URL, admin.site.urls),
]
