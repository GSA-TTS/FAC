from django.db.models import Q
import time
from .search_general import report_timing

import logging

logger = logging.getLogger(__name__)


def search_findings(general_results, params):
    t0 = time.time()
    q = Q()
    findings_fields = params["findings"]

    for field in findings_fields:
        match field:
            case "is_modified_opinion":
                # Are these booleans in the DB? Or, strings?
                q |= Q(finding__is_modified_opinion="Y")
            case "is_other_findings":
                q |= Q(finding__is_other_findings="Y")
            case "is_material_weakness":
                q |= Q(finding__is_material_weakness="Y")
            case "is_significant_deficiency":
                q |= Q(finding__is_significant_deficiency="Y")
            case "is_other_matters":
                q |= Q(finding__is_other_matters="Y")
            case "is_questioned_costs":
                q |= Q(finding__is_questioned_costs="Y")
            case "is_repeat_finding":
                q |= Q(finding__is_repeat_finding="Y")
            case _:
                pass
    filtered_general_results = general_results.filter(q).distinct()

    t1 = time.time()
    report_timing("search_findings", params, t0, t1)
    return filtered_general_results
