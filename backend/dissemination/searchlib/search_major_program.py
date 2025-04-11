from django.db.models import Q

import logging

logger = logging.getLogger(__name__)


def audit_search_major_program(params):
    q = Q()
    major_program_fields = params.get("major_program")
    if "True" in major_program_fields:
        q |= Q(is_major_program=True)
    elif "False" in major_program_fields:
        q |= Q(is_major_program=False)
    return q
