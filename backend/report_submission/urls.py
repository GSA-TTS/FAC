from django.urls import path
from . import views


urlpatterns = [
    # test page
    path("", views.step1.as_view(), name="report_submission"),
    path("step2/", views.EligibilityFormView.as_view(), name="report_eligibility")
]
