from config import settings


def static_site_url(request):
    """
    Returns the STATIC_SITE_URL. This is added to the context of every template request
    made on the site. Used most frequently for links in the primary nav.
    """
    return {"STATIC_SITE_URL": settings.STATIC_SITE_URL}
