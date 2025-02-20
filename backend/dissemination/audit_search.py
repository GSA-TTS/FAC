import logging
import time
from math import ceil

from django.db.models import Q, F

from audit.models import Audit
from audit.models.constants import STATUS, FINDINGS_BITMASK, FINDINGS_FIELD_TO_BITMASK
from dissemination.search_utils import SEARCH_FIELDS, SEARCH_QUERIES
from dissemination.searchlib.search_constants import DIRECTION, ORDER_BY

logger = logging.getLogger(__name__)

def audit_search(params):
    """
    This search is based off the updated 'audit' table rather than the
    dissemination tables.

    TODO: Need to account for Tribal. Remove Logging
    """
    t0 = time.time()
    params = params or dict()
    query = Q(submission_status=STATUS.DISSEMINATED)

    for field in SEARCH_FIELDS:
        if field.value in params and params.get(field.value):
            query = query & SEARCH_QUERIES[field](params)

    # Unfortunately, findings search is a bit different due to using a bit mask
    bitmask = _calculate_bitmask(params)
    results = Audit.objects.all().annotate(
        findings_bitmask=F('findings_summary').bitand(bitmask)
    )
    results = results.filter(query)
    results = _sort_results(results, params)
    logger.error(f"=================== AuditSearch ==========> {results.query}")
    logger.error(f"=================== AuditSearch ==========> {results.count()}")
    t1 = time.time()
    readable = int(ceil((t1 - t0) * 1000))
    logger.error(f"=================== AuditSearch ==========> {readable}ms")
    return results

def _calculate_bitmask(params):
    findings_fields = params.get("findings")
    findings_mask = 0
    if "all_findings" in findings_fields:
        findings_mask = FINDINGS_BITMASK.ALL
    else:
        for mask in FINDINGS_FIELD_TO_BITMASK:
            if mask.search_param in findings_fields:
                findings_mask = findings_mask | mask.mask
    return findings_mask

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
                # Ex. COG-01 -> COG-99, OVER-01 -> OVER-99
                new_results = results.order_by("oversight_agency", "cognizant_agency")
            else:
                # Ex. OVER-99 -> OVER-01, COG-99 -> COG-01
                new_results = results.order_by("-oversight_agency", "-cognizant_agency")
        case _:
            new_results = results.order_by(f"{direction}fac_accepted_date")

    return new_results
