from django.db.models import Q

import logging


logger = logging.getLogger(__name__)


def audit_search_cog_or_oversight(params):
    agency_name = params.get("agency_name", None)
    cog_or_oversight = params.get("cog_or_oversight", None)
    if cog_or_oversight.lower() in ["", "either"]:
        if agency_name:
            return Q(
                Q(cognizant_agency__in=[agency_name])
                | Q(oversight_agency__in=[agency_name])
            )
        else:
            # Every submission should have a value for either cog or over, so
            # nothing to do here
            return Q()
    elif cog_or_oversight.lower() == "cog":
        if agency_name:
            return Q(cognizant_agency__in=[agency_name])
        else:
            # Submissions that have any cog
            return Q(cognizant_agency__isnull=False)
    elif cog_or_oversight.lower() == "oversight":
        if agency_name:
            return Q(oversight_agency__in=[agency_name])
        else:
            # Submissions that have any over
            return Q(oversight_agency__isnull=False)
