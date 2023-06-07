from django.urls import path

from . import views

app_name = "search"

urlpatterns = [
    path("", views.SearchHome.as_view(), name="search"),
    path("<str:search_path>", views.SearchResults.as_view(), name="search_results"),
]
