from django.urls import path
from . import views


urlpatterns = [
    # test page
    path("test/", views.home2.as_view(), name="report_submission"),
]
