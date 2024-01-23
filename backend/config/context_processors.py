from config import settings


def static_site_url(request):
    """
    Returns the STATIC_SITE_URL. This is added to the context of every template request
    made on the site. Used most frequently for links in the primary nav.
    """
    return {"STATIC_SITE_URL": settings.STATIC_SITE_URL}


def omb_num_exp_date(request):
    """
    Returns the OMB_NUMBER (str) and OMB_EXP_DATE (str) in template context form.
    Displayed as a legal requirement on the header of every page.
    """
    return {"OMB_NUMBER": settings.OMB_NUMBER, "OMB_EXP_DATE": settings.OMB_EXP_DATE}


def current_environment(request):
    """
    Returns the OMB_NUMBER (str) and OMB_EXP_DATE (str) in template context form.
    Displayed as a legal requirement on the header of every page.
    """
    return {"ENVIRONMENT": settings.ENVIRONMENT}
