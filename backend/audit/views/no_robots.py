from django.http import HttpResponse


def no_robots(_context):
    """
    Return Disallow for *
    """
    content = "User-agent: *\nDisallow: /"
    return HttpResponse(content, content_type="text/plain")
