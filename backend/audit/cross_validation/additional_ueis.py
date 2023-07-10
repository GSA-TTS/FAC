def additional_ueis(all_sections):
    """
    Checks that there are additional UEIs if
    general_information.multiple_ueis_covered is True, and that there are
    none if it's not True.
    """
    addl_ueis_indicated = all_sections["general_information"].get("multiple_ueis_covered")
    auditee_uei = all_sections["general_information"].get("auditee_uei")
    addl_ueis = all_sections["additional_ueis"]
    if addl_ueis_indicated:
        """
        We need to check that:

        +   all_sections.additional_ueis isn't an empty list
        +   The first object in it has a value for additional_uei
        +   None of the values are the same as auditee_uei
        """
        if not addl_ueis:
            msg = "".join(
                [
                    "general_information.multiple_ueis_covered is checked, ",
                    "but no additonal UEIs were found.",
                ]
            )
            return [{"error": msg}]
        if not addl_ueis[0].get("additional_uei"):
            msg = "".join(
                [
                    "general_information.multiple_ueis_covered is checked, ",
                    "but no additonal UEIs were found.",
                ]
            )
            return [{"error": msg}]
        addl_uei_list = [_["additional_uei"] for _ in addl_ueis]
        if auditee_uei in addl_uei_list:
            msg = "The additional UEIs list includes the auditee UEI."
            return [{"error": msg}]
    else:
        if addl_ueis:
            msg = "".join(
                [
                    "general_information.multiple_ueis_covered is marked false, ",
                    "but additonal UEIs were found.",
                ]
            )
            return [{"error": msg}]

    return []
