import logging

from django.db.models import Q

from audit.models import Audit
from audit.models.constants import STATUS
from dissemination.search_utils import SEARCH_FIELDS, SEARCH_QUERIES

logger = logging.getLogger(__name__)

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
            query = query & SEARCH_QUERIES[field](params)


    results = Audit.objects.filter(query)
    logger.error(f"=================== JASON JASON JASON ==========> {results.query}")
    logger.error(f"=================== JASON JASON JASON ==========> {results.count()}")
