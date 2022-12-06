from django.shortcuts import render  # noqa: F401
from django.views import generic


# class based views for ...
class home2(generic.TemplateView):
    """Basic class for home."""

    template_name = "gen-form.html"
 