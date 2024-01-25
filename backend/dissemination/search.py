import logging
import time
from .search_constants import (
    ORDER_BY,
    DIRECTION,
    DAS_LIMIT
)
from .search_general import (
    report_timing,
    search_general
    )
from .search_alns import (
    search_alns,
    _annotate_findings
)

logger = logging.getLogger(__name__)


#######################
# https://books.agiliq.com/en/latest/README.html
# Their ORM cookbook looks to be useful reading.
# https://books.agiliq.com/projects/django-orm-cookbook/en/latest/subquery.html

def search(params):
    """
    Given any (or no) search fields, build and execute a query on the General table and return the results.
    Empty searches return everything.
    """
    ##############
    # Set defaults for things we definitely want in the params.
    params = _set_general_defaults(params)

    # Time the whole thing.
    t0 = time.time()

    ##############
    # GENERAL
    results = search_general(params)

    ##############
    # Truncate down to the limit
    # This is the stopgap. If we have too many still, we're going
    # to force the issue and truncate the result set.
    # https://docs.djangoproject.com/en/4.2/topics/db/queries/#limiting-querysets
    results = _sort_results(results, params)
    results = search_alns(results, params)
    
    t1 = time.time()
    report_timing("search", params, t0, t1)
    return results

def _set_general_defaults(params):
    #############
    # Set some defaults.

    # Let's make sure we have a confirmation that
    # we default to not sharing data marked as suppressed.
    if not params.get("include_private"):
        params["include_private"] = False

    # Set default order direction
    if not params.get("order_by", None):
        params["order_by"] = ORDER_BY.fac_accepted_date
    if not params.get("order_direction", None):
        params["order_direction"] = DIRECTION.descending

    params["LIMIT"] = DAS_LIMIT

    return params

def _sort_results(results, params):
    # Instead of nesting conditions, we'll prep a string
    # for determining the sort direction.
    
    match params.get("order_direction"):
        case DIRECTION.ascending:
            direction = ""
        case _:
            direction = "-"

    # Now, apply the sort that we pass in front the front-end.
    match params.get("order_by"):
        case ORDER_BY.auditee_name:
            new_results = results.order_by(f"{direction}auditee_name")
        case ORDER_BY.auditee_uei:
            new_results = results.order_by(f"{direction}auditee_uei")
        case ORDER_BY.fac_accepted_date:
            new_results = results.order_by(f"{direction}fac_accepted_date")
        case ORDER_BY.audit_year:
            new_results = results.order_by(f"{direction}audit_year")
        case ORDER_BY.cog_over:
            if params.get("order_direction") == DIRECTION.ascending:
                new_results = results.order_by("cognizant_agency")
            else:
                new_results = results.order_by("oversight_agency")
        case _:
            new_results = results.order_by(f"{direction}fac_accepted_date")

    return new_results

