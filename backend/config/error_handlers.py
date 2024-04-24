from django.shortcuts import render


def handler404(request, exception, template_name="404.html"):
    """
    Custom handler for 404. Ensures the 404 template loads with proper context (environment, login info, OMB values).
    """
    return render(request, template_name, {}, status=404)


def handler403(request, exception, template_name="403.html"):
    """
    Custom handler for 403. Ensures the 403 template loads with proper context (environment, login info, OMB values).
    """
    return render(request, template_name, {}, status=403)


def handler500(request, template_name="500.html"):
    """
    Custom handler for 500s. Ensures the 500 template loads with proper context (environment, login info, OMB values).
    """
    return render(request, template_name, {}, status=500)


def handler400(request, exception, template_name="400.html"):
    """
    Custom handler for 400. Ensures the 400 template loads with proper context (environment, login info, OMB values).
    """
    return render(request, template_name, {}, status=400)
