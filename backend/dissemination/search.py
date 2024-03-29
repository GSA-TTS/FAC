import logging
import time
from .searchlib.search_constants import ORDER_BY, DIRECTION, DAS_LIMIT
from .searchlib.search_general import report_timing, search_general
from .searchlib.search_alns import search_alns
from .searchlib.search_findings import search_findings
from .searchlib.search_direct_funding import search_direct_funding
from .searchlib.search_major_program import search_major_program
from dissemination.models import DisseminationCombined, General

logger = logging.getLogger(__name__)


#######################
# https://books.agiliq.com/en/latest/README.html
# Their ORM cookbook looks to be useful reading.
# https://books.agiliq.com/projects/django-orm-cookbook/en/latest/subquery.html

# {'alns': [], -- DisseminationCombined
#  'names': ['AWESOME'], -- General
#  'uei_or_eins': [],  -- General
#  'start_date': None,  -- General
#  'end_date': None,  -- General
#  'cog_or_oversight': '', -- General, but not wanted
#  'agency_name': '',  -- NO IDEA
#  'audit_years': [], -- General
#  'findings': [], -- DisseminationCombined
#  'direct_funding': [], -- DisseminationCombined
#  'major_program': [], -- DisseminationCombined
#  'auditee_state': '', -- General
#  'order_by': -- General
#  'fac_accepted_date', -- General
#  'order_direction': -- General
#  'descending', 'LIMIT': 1000} -- General


def is_advanced_search(params_dict):
    return params_dict.get("advanced_search_flag")


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

    logger.info(params)
    if is_advanced_search(params):
        logger.info("search Searching `DisseminationCombined`")
        results = search_general(DisseminationCombined, params)
        results = _sort_results(results, params)
        results = search_alns(results, params)
        results = search_findings(results, params)
        results = search_direct_funding(results, params)
        results = search_major_program(results, params)
    else:
        logger.info("search Searching `General`")
        results = search_general(General, params)
        results = _sort_results(results, params)

    results = results.distinct("report_id", params.get("order_by", "fac_accepted_date"))

    t1 = time.time()
    report_timing("search", params, t0, t1)
    return results


def _set_general_defaults(params):
    #############
    # Set some defaults.
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
