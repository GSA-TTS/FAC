from .warnings import warn_auditee_auditor_ein_match


def check_auditee_auditor_ein_match(sac_dict, *_args, **_kwargs):
    """
    Warns if the auditee EIN and auditor EIN are identical.

    If either or both EINs are absent, no warning is raised.
    """
    all_sections = sac_dict["sf_sac_sections"]
    general_information = all_sections.get("general_information", {})

    auditee_ein = general_information.get("ein")
    auditor_ein = general_information.get("auditor_ein")

    if auditee_ein and auditor_ein and auditee_ein == auditor_ein:
        return [{"warning": warn_auditee_auditor_ein_match()}]

    return []
