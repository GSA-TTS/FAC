from django.db.models import Q

import logging

logger = logging.getLogger(__name__)


def audit_search_passthrough_name(params):
    q = Q()
    passthrough_names = params.get("passthrough_name")
    for term in passthrough_names:
        q_sub = Q()
        for sub in term.split():
            q_sub.add(Q(passthrough_names__icontains=sub), Q.AND)
        q.add(q_sub, Q.OR)
    return q
