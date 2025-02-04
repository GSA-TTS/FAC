import logging
from enum import Enum

from django.db.models import Q

from audit.models import Audit
from audit.models.constants import STATUS
from dissemination.search_utils import _get_names_match_query

logger = logging.getLogger(__name__)

class SEARCH_FIELDS(Enum):
    AUDIT_YEARS = "audit_years"
    AUDITEE_STATE = "auditee_state"
    NAMES = "names"
    UEI_EIN = "uei_or_eins"
    START_DATE = "start_date"
    END_DATE = "end_date"
    FY_END_MONTH = "fy_end_month"
    ENTITY_TYPE = "entity_type"
    REPORT_ID = "report_id"

SEARCH_QUERIES = {
    SEARCH_FIELDS.AUDIT_YEARS: lambda audit_years : Q(audit__audit_year__in=audit_years),
    SEARCH_FIELDS.AUDITEE_STATE: lambda auditee_state : Q(audit__general_information__auditee_state__in=[auditee_state]),
    SEARCH_FIELDS.NAMES: _get_names_match_query, # TODO Move this.
    SEARCH_FIELDS.UEI_EIN: lambda uei_ein : Q(audit__general_information__auditee_ein__in=uei_ein) |
                                            Q(audit__general_information__auditee_uei__in=uei_ein) |
                                            Q(audit__additional_eins__contains=uei_ein) |
                                            Q(audit__additional_ueis__contains=uei_ein),
    SEARCH_FIELDS.START_DATE: lambda start_date : Q(audit__fac_accepted_date__gte=start_date),
    SEARCH_FIELDS.END_DATE: lambda end_date : Q(audit__fac_accepted_date__lte=end_date),
    SEARCH_FIELDS.FY_END_MONTH: lambda fy_end_month : Q(audit__fy_end_month=fy_end_month),
    SEARCH_FIELDS.ENTITY_TYPE: lambda entity_type: Q(audit__general_information__user_provided_organization_type__in=entity_type),
    SEARCH_FIELDS.REPORT_ID: lambda report_id : Q(report_id=report_id),
}

def audit_search(params):
    """
    This search is based off the updated 'audit' table rather than the
    dissemination tables.

    TODO: Need to account for Tribal.
    """
    params = params or dict()
    query = Q(submission_status=STATUS.DISSEMINATED)

    for field in SEARCH_FIELDS:
        if field.value in params and params.get(field.value):
            query = query & SEARCH_QUERIES[field](params.get(field.value))

    results = Audit.objects.filter(query)
    logger.error(f"=================== JASON JASON JASON ==========> {results.count()}")
    logger.error(f"=================== JASON JASON JASON ==========> {results.query}")
