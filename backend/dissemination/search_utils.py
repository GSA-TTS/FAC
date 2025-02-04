from django.db.models import Q

def _get_names_match_query(names_list):
    """
    Given a list of (potential) names, return the query object that searches auditee and firm names.
    """
    if not names_list:
        return Q()

    # TODO: Confirm
    name_fields = [
        # "auditee_city",
        "general_information__auditee_contact_name",
        "auditee_certification__auditee_name",
        "general_information__auditee_contact_name__auditee_email",
        "general_information__auditee_name",
        "general_information__auditor_contact_name",
        "auditor_certification__auditor_signature__auditor_name",
        "general_information__auditor_email",
        "general_information__auditor_firm_name",
    ]

    names_match = Q()

    # The search terms are coming in as a string in a list.
    # E.g. the search text "college berea" returns nothing,
    # when it should return entries for "Berea College". That is
    # because it comes in as
    # ["college berea"]
    #
    # This has to be flattened to a list of singleton terms.
    flattened = []
    for term in names_list:
        for sub in term.split():
            flattened.append(sub)

    # Now, for each field (e.g. "auditee_contact_name")
    # build up an AND over the terms. We want something where all of the
    # terms appear.
    # Then, do an OR over all of the fields. If that combo appears in
    # any of the fields, we want to return it.
    for field in name_fields:
        field_q = Q()
        for name in flattened:
            field_q.add(Q(**{f"audit__{field}__icontains": name}), Q.AND)
        names_match.add(field_q, Q.OR)

    # Now, "college berea" and "university state ohio" return
    # the appropriate terms. It is also significantly faster than what
    # we had before.

    return names_match
