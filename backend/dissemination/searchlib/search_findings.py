from django.db.models import Q
import time
from .search_general import report_timing

import logging

logger = logging.getLogger(__name__)


def search_findings(general_results, params):
    t0 = time.time()
    q = Q()
    findings_fields = params.get("findings", [])

    for field in findings_fields:
        match field:
            case "all_findings":
                # This can be achieved via federalaward__findings_count__gt=0,
                # But, it's faster to chain ORs in the Finding table than it is to walk the FederalAward table.
                q |= Q(is_modified_opinion="Y")
                q |= Q(is_other_findings="Y")
                q |= Q(is_material_weakness="Y")
                q |= Q(is_significant_deficiency="Y")
                q |= Q(is_other_matters="Y")
                q |= Q(is_questioned_costs="Y")
                q |= Q(is_repeat_finding="Y")
            case "is_modified_opinion":
                q |= Q(is_modified_opinion="Y")
            case "is_other_findings":
                q |= Q(is_other_findings="Y")
            case "is_material_weakness":
                q |= Q(is_material_weakness="Y")
            case "is_significant_deficiency":
                q |= Q(is_significant_deficiency="Y")
            case "is_other_matters":
                q |= Q(is_other_matters="Y")
            case "is_questioned_costs":
                q |= Q(is_questioned_costs="Y")
            case "is_repeat_finding":
                q |= Q(is_repeat_finding="Y")
            case _:
                pass
    filtered_general_results = general_results.filter(q)

    t1 = time.time()
    report_timing("search_findings", params, t0, t1)
    return filtered_general_results
