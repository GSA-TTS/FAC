from django.db.models import Q

import logging

logger = logging.getLogger(__name__)


def audit_search_direct_funding(params):
    q = Q()
    direct_funding_fields = params.get("direct_funding")
    for field in direct_funding_fields:
        match field:
            case "direct_funding":
                q |= Q(has_direct_funding=True)
            case "passthrough_funding":
                q |= Q(has_indirect_funding=True)
            case _:
                pass
    return q
