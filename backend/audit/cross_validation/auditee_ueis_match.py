from .errors import err_auditee_ueis_match


def auditee_ueis_match(sac_dict):
    """Checks that the auditee_uei values in each sheet are the same."""
    all_sections = sac_dict["sf_sac_sections"]
    sections = filter(None, all_sections.values())
    ueis = list(filter(None, (s.get("auditee_uei", None) for s in sections)))
    if len(set(ueis)) > 1:
        return [{"error": err_auditee_ueis_match()}]
    return []
