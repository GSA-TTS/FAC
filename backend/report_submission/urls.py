from django.urls import path
from . import views


urlpatterns = [
    # test page
    path("", views.Step.as_view(), name="step"),
    # path("step2/", views.EligibilityFormView.as_view(), name="report_eligibility")
]
