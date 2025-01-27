from datetime import datetime, timezone

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


def navigation_content(request):
    """
    Returns the tree of navigation links. This is added to the context of every template
    request made on the site.
    """
    STATIC_URL = settings.STATIC_SITE_URL

    return {
        "STATIC_SITE_NAVIGATION": [
            {
                "id": "search",
                "name": "Audit search",
                "links": [
                    {
                        "name": "Search",
                        "link": "/dissemination/search",
                    },
                    {
                        "name": "Search resources",
                        "link": f"{STATIC_URL}search-resources",
                    },
                    {
                        "name": "Developer resources",
                        "link": f"{STATIC_URL}api/",
                    },
                    {
                        "name": "Data reliability",
                        "link": f"{STATIC_URL}data-reliability/",
                    },
                    {
                        "name": "Tribal Audits",
                        "link": f"{STATIC_URL}tribal/",
                    },
                ],
            },
            {
                "id": "submission",
                "name": "Audit submission",
                "links": [
                    {
                        "name": "Submission resources",
                        "link": f"{STATIC_URL}audit-resources/",
                    },
                    {
                        "name": "Submission home",
                        "link": "/openid/login",
                    },
                ],
            },
            {
                "id": "updates",
                "name": "Updates & News",
                "links": [
                    {
                        "name": "FAC updates",
                        "link": f"{STATIC_URL}updates/",
                    },
                    {
                        "name": "OMB announcements",
                        "link": f"{STATIC_URL}omb/",
                    },
                    {
                        "name": "System status",
                        "link": f"{STATIC_URL}status/",
                    },
                ],
            },
            {
                "id": "policy",
                "name": "Policy & Compliance",
                "links": [
                    {
                        "name": "Compliance",
                        "link": f"{STATIC_URL}compliance/",
                    },
                    {
                        "name": "Uniform guidance",
                        "link": f"{STATIC_URL}uniform-guidance/",
                    },
                    {
                        "name": "Burden statement",
                        "link": f"{STATIC_URL}audit-resources/burden-statement/",
                    },
                ],
            },
            {
                "id": "contact",
                "name": "Contacts",
                "links": [
                    {
                        "name": "FAC Helpdesk",
                        "link": "https://support.fac.gov/hc/en-us",
                    },
                    {
                        "name": "Contact resources",
                        "link": f"{STATIC_URL}contact-resources/",
                    },
                    {
                        "name": "Cognizant agency contacts",
                        "link": f"{STATIC_URL}contact-resources/cognizant-agency-contacts/",
                    },
                    {
                        "name": "NSAC and KMSAL contacts",
                        "link": f"{STATIC_URL}assets/agency-contacts/2024-agency-contacts.pdf",
                    },
                ],
            },
        ]
    }
