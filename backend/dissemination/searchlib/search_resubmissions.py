from django.db.models import Q

from .search_general import report_timing
from audit.models.constants import RESUBMISSION_STATUS
from users.permissions import is_federal_user

import logging
import time

logger = logging.getLogger(__name__)


def search_resubmissions(request, general_results, params):
    """
    Searches on General column 'resubmission_status'. Comes in as True/False, to
    search on including/excluding deprecated submissions.
    """
    t0 = time.time()
    q = Q()
    resubmission_fields = params.get("resubmissions", "exclude")

    # Always exclude deprecated submissions if NOT a Fed
    # Also exclude if selected in the filter
    if not is_federal_user(request.user) or "exclude" in resubmission_fields:
        q = ~Q(resubmission_status=RESUBMISSION_STATUS.DEPRECATED)

    filtered_general_results = general_results.filter(q).distinct()

    t1 = time.time()
    report_timing("search_resubmission", params, t0, t1)

    return filtered_general_results
