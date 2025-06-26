from .errors import (
    err_additional_eins_empty,
    err_additional_eins_has_auditee_ein,
    err_additional_eins_not_empty,
)


def check_additional_eins(sac_dict, *_args, **_kwargs):
    """
    Checks that there are additional EINs if
    general_information.multiple_eins_covered is True, and that there are
    none if it's not True.
    """
    all_sections = sac_dict["sf_sac_sections"]
    addl_eins_checked = all_sections["general_information"].get("multiple_eins_covered")
    auditee_ein = all_sections["general_information"].get("auditee_ein")
    
    addl_eins = []
    if all_sections.get("additional_eins"):
        addl_eins = all_sections.get("additional_eins", {}).get(
            "additional_eins_entries"
        )
    
    if addl_eins_checked:
        """
        We need to check that:

        +   all_sections.additional_eins isn't an empty list
        +   The first object in it has a value for additional_ein
        +   None of the values are the same as auditee_ein
        """
        if not addl_eins:
            return [{"error": err_additional_eins_empty()}]
        if not addl_eins[0]:
            return [{"error": err_additional_eins_empty()}]
        addl_ein_list = [_["additional_ein"] for _ in addl_eins]
        if auditee_ein in addl_ein_list:
            return [{"error": err_additional_eins_has_auditee_ein()}]
    else:
        if addl_eins:
            return [{"error": err_additional_eins_not_empty()}]

    return []
