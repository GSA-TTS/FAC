from django.urls import path
from . import views


urlpatterns = [
    # test page
    path("", views.step1.as_view(), name="step-1"),
    #path("step2/", views.EligibilityFormView.as_view(), name="report_eligibility")
    path("step-2/", views.step2.as_view(), name="step-2"),
    path("step-3/", views.step3.as_view(), name="step-3"),
]
