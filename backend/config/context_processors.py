from config import settings
from datetime import datetime, timezone
from django.contrib.sessions.models import Session


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
    Returns the ENVIRONMENT (str) in template context form.
    Used in determining the display of the TEST SITE Banner.
    """
    return {"ENVIRONMENT": settings.ENVIRONMENT}


def maintenance_banner(request):
    """
    Returns maintenance banner template context.
    MAINTENANCE_BANNER is True if the banner should be displaying and False if not, based on settings.MAINTENANCE_BANNER_DATES.
    MAINTENANCE_BANNER_START_TIME and MAINTENANCE_BANNER_END_TIME are None if the banner does not display.
    MAINTENANCE_BANNER_MESSAGE is included if it exists alongside the banner dates.
    """
    current_time = datetime.now(timezone.utc)
    context = {
        "MAINTENANCE_BANNER": False,
    }

    # For every designated date range:
    # If any start or end time is unavailable, something is misconfigured. So, disable the banner.
    # If we are within the specified timeframes, enable the banner.
    for date_range in settings.MAINTENANCE_BANNER_DATES:
        start_time = date_range.get("start")
        end_time = date_range.get("end")

        if not start_time or not end_time:
            return context

        if current_time > start_time and current_time < end_time:
            context["MAINTENANCE_BANNER"] = True
            context = context | {
                "MAINTENANCE_BANNER_START_TIME": start_time,
                "MAINTENANCE_BANNER_END_TIME": end_time,
                "MAINTENANCE_BANNER_MESSAGE": date_range.get("message", ""),
            }
            return context

    # Base case - we are not within any of the given timeframes. Disable the banner.
    return context

# Helper function to format time
def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes} minutes, {seconds} seconds"

# Update the context processor
def session_timeout_warning(request=None, session_expired=False):

    if request is not None and not isinstance(request, bool):
        session_expired = not (hasattr(request, "user") and request.user.is_authenticated)

    if not isinstance(session_expired, bool):
        raise ValueError("session_expired must be a boolean value.")

    return {
        "session_expired": session_expired,
    }


