from django.views import generic
from django.shortcuts import render, redirect
from django.urls import reverse


# class based views for posts
class Home(generic.View):
    """
    This is for the root path: /

    It will return the home template if not authenticated and the audit table if
    authenticated.
    """

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            url = reverse("audit:MySubmissions")
            return redirect(url)
        template_name = "home.html"
        extra_context = {}
        return render(request, template_name, extra_context)
