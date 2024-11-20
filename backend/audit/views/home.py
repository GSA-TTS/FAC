from datetime import datetime, timezone
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic


# class based views for posts
class Home(generic.View):
    """
    This is for the root path: /

    It will return the home template if not authenticated and the audit table if
    authenticated.
    """

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and not settings.DISABLE_AUTH:
            url = reverse("audit:MySubmissions")
            return redirect(url)
        template_name = "home.html"
        extra_context = {"DISABLE_AUTH": settings.DISABLE_AUTH}
        return render(request, template_name, extra_context)


class Maintenance(generic.View):
    """
    This is the redirected path for Maintenance mode.

    It will return the home template with an error status for every single request
    so long as maintenance is enabled.
    """

    def get(self, request, *args, **kwargs):
        template_name = "503.html"

        current_time = datetime.now(timezone.utc)
        for date_range in settings.MAINTENANCE_BANNER_DATES:
            if current_time > date_range.get("start") and current_time < date_range.get("end"):
                template_name = date_range.get("template_name", "503.html")
        
        return render(request, template_name)
