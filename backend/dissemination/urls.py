from django.urls import path

from dissemination import views

app_name = "dissemination"

urlpatterns = [
    path("search", views.Search.as_view(), name="Search"),
    path("search/<str:search_id>", views.SavedSearch.as_view(), name="SavedSearch"),
]
