from django.db.models import Q


def audit_search_compliance_requirement(params):
    q = Q()
    crs = params.get("type_requirement")
    for cr in crs:
        q_sub = Q()
        for sub in cr.split():
            q_sub.add(Q(compliance_requirements__icontains=sub), Q.AND)
        q.add(q_sub, Q.OR)
    return q if crs else Q()
