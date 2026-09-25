from config import settings

from support.models.maintenance_banner import MaintenanceBanner


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
                        "name": "Tribal audit search",
                        "link": f"{STATIC_URL}tribal",
                    },
                    {
                        "name": "Search resources",
                        "link": f"{STATIC_URL}search-resources",
                    },
                ],
            },
            {
                "id": "submission",
                "name": "Audit submission",
                "links": [
                    {
                        "name": "Submit an audit",
                        "link": "/openid/login",
                    },
                    {
                        "name": "Submission resources",
                        "link": f"{STATIC_URL}audit-resources/",
                    },
                    {
                        "name": "Submission guide",
                        "link": f"{STATIC_URL}audit-resources/how-to",
                    },
                    {
                        "name": "SF-SAC workbooks",
                        "link": f"{STATIC_URL}audit-resources/sf-sac",
                    },
                ],
            },
            {
                "id": "data",
                "name": "Data",
                "links": [
                    {"name": "About the data", "link": f"{STATIC_URL}data"},
                    {"name": "Download CSV data", "link": f"{STATIC_URL}data/download"},
                    {"name": "Developer API resources", "link": f"{STATIC_URL}api"},
                    {
                        "name": "Data reliability",
                        "link": f"{STATIC_URL}data/reliability",
                    },
                    {
                        "name": "Data curation",
                        "link": f"{STATIC_URL}data/reliability/curation",
                    },
                    {"name": "Data migration", "link": f"{STATIC_URL}data/migration"},
                ],
            },
            {
                "id": "updates",
                "name": "Updates & News",
                "links": [
                    {
                        "name": "FAC updates",
                        "link": f"{STATIC_URL}updates",
                    },
                    {
                        "name": "OMB announcements",
                        "link": f"{STATIC_URL}omb",
                    },
                    {
                        "name": "System status",
                        "link": f"{STATIC_URL}status",
                    },
                ],
            },
            {
                "id": "policy",
                "name": "Policy & Compliance",
                "links": [
                    {
                        "name": "Compliance",
                        "link": f"{STATIC_URL}compliance",
                    },
                    {
                        "name": "Uniform guidance",
                        "link": f"{STATIC_URL}uniform-guidance",
                    },
                    {
                        "name": "FAC Burden statement",
                        "link": f"{STATIC_URL}audit-resources/burden-statement",
                    },
                ],
            },
            {
                "id": "contact",
                "name": "Contacts",
                "links": [
                    {
                        "name": "Contact resources",
                        "link": f"{STATIC_URL}contact-resources",
                    },
                    {
                        "name": "FAC Helpdesk",
                        "link": "https://support.fac.gov/hc/en-us",
                    },
                    {
                        "name": "Cognizant agency contacts",
                        "link": f"{STATIC_URL}contact-resources/cognizant-agency-contacts",
                    },
                    {
                        "name": "NSAC and KMSAL contacts",
                        "link": f"{STATIC_URL}assets/agency-contacts/2024-agency-contacts.pdf",
                    },
                ],
            },
        ]
    }


def active_maintenance_banner(request):
    banner = MaintenanceBanner.objects.first()

    # If a banner exists and its current schedule/status is valid, pass it to templates
    if banner and banner.is_currently_active:
        return {"active_maintenance_banner": banner}
    else:
        return {"active_maintenance_banner": None}
