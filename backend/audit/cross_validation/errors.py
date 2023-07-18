def err_additional_ueis_empty():
    return "".join(
        [
            "general_information.multiple_ueis_covered is checked, ",
            "but no additonal UEIs were found.",
        ]
    )


def err_additional_ueis_has_auditee_uei():
    return "The additional UEIs list includes the auditee UEI."


def err_additional_ueis_not_empty():
    return "".join(
        [
            "general_information.multiple_ueis_covered is marked false, ",
            "but additonal UEIs were found.",
        ]
    )


def err_auditee_ueis_match():
    return "Not all auditee UEIs matched."
