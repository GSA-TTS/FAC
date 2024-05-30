import logging
import time
from .searchlib.search_constants import ORDER_BY, DIRECTION, DAS_LIMIT
from .searchlib.search_general import report_timing, search_general
from .searchlib.search_alns import search_alns
from .searchlib.search_findings import search_findings
from .searchlib.search_direct_funding import search_direct_funding
from .searchlib.search_major_program import search_major_program
from .searchlib.search_type_requirement import search_type_requirement
from .searchlib.search_passthrough_name import search_passthrough_name
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
    """
    Returns True if the 'advanced_search_flag' param is True.
    """
    return params_dict.get("advanced_search_flag", False)


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
        results = search_alns(results, params)
        results = search_findings(results, params)
        results = search_direct_funding(results, params)
        results = search_major_program(results, params)
        results = search_type_requirement(results, params)
        results = search_passthrough_name(results, params)
    else:
        logger.info("search Searching `General`")
        results = search_general(General, params)

    results = _sort_results(results, params)
    results = _make_distinct(results, params)

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
    """
    Append an `.order_by()` to the results based on the 'order_by' and 'order_direction' params.
    The 'cog_over' input field is split into its appropriate DB fields.
    """
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
                # Ex. COG-01, COG-99, OVER-01, OVER-99
                new_results = results.order_by("cognizant_agency", "oversight_agency")
            else:
                # Ex. OVER-01, OVER-99, COG-01, COG-99
                new_results = results.order_by("oversight_agency", "cognizant_agency")
        case _:
            new_results = results.order_by(f"{direction}fac_accepted_date")

    return new_results


def _make_distinct(results, params):
    """
    Append a `.distinct()` to the results QuerySet, to prevent duplicate results.
    Rows with duplicate report_ids exist when using AdvancedSearch/DisseminationCombined.
    """
    order_by = params.get("order_by", "fac_accepted_date")
    order_direction = params.get("order_direction", "")

    # cog_over needs to be broken out here in the same order it is broken out in _sort_results().
    if order_by == "cog_over" and order_direction == "ascending":
        results = results.distinct("report_id", "cognizant_agency", "oversight_agency")
    elif order_by == "cog_over":
        results = results.distinct("report_id", "oversight_agency", "cognizant_agency")
    else:
        results = results.distinct("report_id", order_by)

    return results
