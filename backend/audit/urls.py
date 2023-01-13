from django.urls import path
from . import views


urlpatterns = [
    path("", views.MySubmissions.as_view(), name="MySubmissions"),
]
