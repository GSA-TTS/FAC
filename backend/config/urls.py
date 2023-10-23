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
    path(
        "api/sac/ueivalidation",
        views.UEIValidationFormView.as_view(),
        name="api-uei-validation",
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
