from api import views
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

#  DRF API views
api_router = routers.DefaultRouter()
api_router.register(r'sf-sac', views.SACViewSet)

schema_view = get_schema_view(
    title='Federal Audit Clearinghouse API',
    version=settings.API_VERSION,
    url='http://localhost:8000/api/',
    renderer_classes=[JSONOpenAPIRenderer]
)

urlpatterns = [
    path('api/schema.json', schema_view),
    path('api/', include(api_router.urls)),
    path('sac/eligibility', views.EligibilityFormView.as_view(), name='eligibility'),
    path('sac/generalinfo', views.GeneralInfoView.as_view(), name='general-info'),
    path('sac/orgtypes', views.OrgTypesView.as_view(), name='org-types'),
    path(settings.ADMIN_URL, admin.site.urls),
]
