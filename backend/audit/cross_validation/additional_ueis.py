from .errors import (
    err_additional_ueis_empty,
    err_additional_ueis_has_auditee_uei,
    err_additional_ueis_not_empty,
)


def additional_ueis(sac_dict):
    """
    Checks that there are additional UEIs if
    general_information.multiple_ueis_covered is True, and that there are
    none if it's not True.
    """
    all_sections = sac_dict["sf_sac_sections"]
    addl_ueis_checked = all_sections["general_information"].get("multiple_ueis_covered")
    auditee_uei = all_sections["general_information"].get("auditee_uei")
    addl_ueis = (
        all_sections["additional_ueis"]
        .get("AdditionalUEIs", {})
        .get("additional_ueis_entries")
    )
    if addl_ueis_checked:
        """
        We need to check that:

        +   all_sections.additional_ueis isn't an empty list
        +   The first object in it has a value for additional_uei
        +   None of the values are the same as auditee_uei
        """
        if not addl_ueis:
            return [{"error": err_additional_ueis_empty()}]
        if not addl_ueis[0]:
            return [{"error": err_additional_ueis_empty()}]
        addl_uei_list = [_["additional_uei"] for _ in addl_ueis]
        if auditee_uei in addl_uei_list:
            return [{"error": err_additional_ueis_has_auditee_uei()}]
    else:  # addl_ueis_checked is false
        if addl_ueis:
            return [{"error": err_additional_ueis_not_empty()}]

    return []
