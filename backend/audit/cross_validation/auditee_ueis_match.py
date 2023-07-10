def auditee_ueis_match(all_sections):
    """Checks that the auditee_uei values in each sheet are the same."""
    sections = filter(None, all_sections.values())
    ueis = list(filter(None, (s.get("auditee_uei", None) for s in sections)))
    if len(set(ueis)) != 1:
        return [{"error": "Not all auditee UEIs matched."}]
    return []
