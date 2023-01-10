from django.urls import path
from . import views


urlpatterns = [
    # home page
    path("", views.Home.as_view(), name="Home"),
    # route for posts
    # path("<slug:slug>/", views.postdetail.as_view(), name="post_detail"),
]
