from .errors import (
    err_secondary_auditors_empty,
    err_secondary_auditors_not_empty,
)


def check_secondary_auditors(sac_dict, *_args, **_kwargs):
    """
    Checks that there are secondary auditors if
    general_information.secondary_auditors_exist is True, and that there are
    none if it's not True.
    """
    all_sections = sac_dict["sf_sac_sections"]
    sec_aud_checked = all_sections["general_information"].get("secondary_auditors_exist")
    
    sec_auds = all_sections.get("secondary_auditors", {}).get(
        "secondary_auditors_entries"
    )
    
    # If secondary_auditors_exist is checked True, then make sure the workbook was provided.
    # If secondary_auditors_exist is unchecked, make sure the workbook is not present.
    if sec_aud_checked:
        if not sec_auds:
            return [{"error": err_secondary_auditors_empty()}]
        if not sec_auds[0]:
            return [{"error": err_secondary_auditors_empty()}]
    else:
        if sec_auds:
            return [{"error": err_secondary_auditors_not_empty()}]

    return []
