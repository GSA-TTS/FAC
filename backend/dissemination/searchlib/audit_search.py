import logging

from django.db.models import Q, F

from audit.models import Audit
from audit.models.constants import STATUS, FindingsBitmask, FINDINGS_FIELD_TO_BITMASK
from dissemination.searchlib.search_alns import audit_search_alns
from dissemination.searchlib.search_cog_or_oversight import (
    audit_search_cog_or_oversight,
)
from dissemination.searchlib.search_compliance_requirements import (
    audit_search_compliance_requirement,
)

from dissemination.searchlib.search_constants import Direction, OrderBy, SearchFields
from dissemination.searchlib.search_direct_funding import audit_search_direct_funding
from dissemination.searchlib.search_federal_program_name import (
    audit_search_federal_program_name,
)
from dissemination.searchlib.search_major_program import audit_search_major_program
from dissemination.searchlib.search_names import audit_search_names
from dissemination.searchlib.search_passthrough_name import (
    audit_search_passthrough_name,
)
from dissemination.searchlib.search_uei_ein import audit_search_uei_ein

logger = logging.getLogger(__name__)

SEARCH_QUERIES = {
    SearchFields.alns: audit_search_alns,
    SearchFields.audit_years: lambda params: Q(
        audit_year__in=params.get(SearchFields.audit_years.value)
    ),
    SearchFields.auditee_state: lambda params: Q(
        auditee_state__in=[params.get(SearchFields.auditee_state.value)]
    ),
    SearchFields.cog_oversight: audit_search_cog_or_oversight,
    SearchFields.direct_funding: audit_search_direct_funding,
    SearchFields.end_date: lambda params: Q(
        fac_accepted_date__date__lte=params.get(SearchFields.end_date.value)
    ),
    SearchFields.entity_type: lambda params: Q(
        organization_type__in=params.get(SearchFields.entity_type.value)
    ),
    SearchFields.federal_program_name: audit_search_federal_program_name,
    SearchFields.findings: lambda params: (
        Q(findings_bitmask__gt=0) if params.get("findings") else Q()
    ),
    SearchFields.fy_end_month: lambda params: Q(
        fy_end_month=params.get(SearchFields.fy_end_month.value)
    ),
    SearchFields.major_program: audit_search_major_program,
    SearchFields.names: audit_search_names,
    SearchFields.passthrough_name: audit_search_passthrough_name,
    SearchFields.report_id: lambda params: Q(
        report_id__in=params.get(SearchFields.report_id.value)
    ),
    SearchFields.start_date: lambda params: Q(
        fac_accepted_date__date__gte=params.get(SearchFields.start_date.value)
    ),
    SearchFields.type_requirement: audit_search_compliance_requirement,
    SearchFields.uei_ein: audit_search_uei_ein,
}


def search(params):
    """
    This search is based off the updated 'audit' table rather than the
    dissemination tables.
    """
    params = params or dict()
    query = Q(submission_status=STATUS.DISSEMINATED)

    for field in SearchFields:
        if field.value in params and params.get(field.value):
            query = query & SEARCH_QUERIES[field](params)

    # Unfortunately, findings search is a bit different due to using a bit mask
    bitmask = _calculate_bitmask(params)
    results = Audit.objects.all().annotate(
        findings_bitmask=F("findings_summary").bitand(bitmask)
    )
    results = results.filter(query)
    results = _sort_results(results, params)
    return results


def _calculate_bitmask(params):
    findings_fields = params.get("findings")
    findings_mask = 0
    if "all_findings" in findings_fields:
        findings_mask = FindingsBitmask.ALL
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
        case Direction.ascending:
            direction = ""
        case _:
            direction = "-"

    # Now, apply the sort that we pass in front the front-end.
    match params.get("order_by"):
        case OrderBy.auditee_name:
            new_results = results.order_by(f"{direction}auditee_name")
        case OrderBy.auditee_uei:
            new_results = results.order_by(f"{direction}auditee_uei")
        case OrderBy.fac_accepted_date:
            new_results = results.order_by(f"{direction}fac_accepted_date")
        case OrderBy.audit_year:
            new_results = results.order_by(f"{direction}audit_year")
        case OrderBy.cog_over:
            if params.get("order_direction") == Direction.ascending:
                # Ex. COG-01 -> COG-99, OVER-01 -> OVER-99
                new_results = results.order_by("oversight_agency", "cognizant_agency")
            else:
                # Ex. OVER-99 -> OVER-01, COG-99 -> COG-01
                new_results = results.order_by("-oversight_agency", "-cognizant_agency")
        case _:
            new_results = results.order_by(f"{direction}fac_accepted_date")

    return new_results
