from django.shortcuts import render


def handler500(request, template_name="500.html"):
    """
    Custom handler for 500s. Ensures the 500 template loads with proper context (environment, login info, OMB values).
    """
    return render(request, template_name, {})
