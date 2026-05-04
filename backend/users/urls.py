from django.urls import path
from .views import subscribe_view, subscribe_thanks_view

urlpatterns = [
    path('subscribe/', subscribe_view, name='subscribe'),
    path('subscribe/thanks/', subscribe_thanks_view, name='subscribe_thanks'),
]
