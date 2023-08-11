def err_additional_ueis_empty():
    return (
        "general_information.multiple_ueis_covered is checked, "
        "but no additonal UEIs were found."
    )


def err_additional_ueis_has_auditee_uei():
    return "The additional UEIs list includes the auditee UEI."


def err_additional_ueis_not_empty():
    return (
        "general_information.multiple_ueis_covered is marked false, "
        "but additonal UEIs were found."
    )


def err_auditee_ueis_match():
    return "Not all auditee UEIs matched."


def err_awards_findings_but_no_findings_text():
    return "There are findings indicated in Federal Awards but" "none in Findings Text."


def err_missing_tribal_data_sharing_consent():
    return (
        "As a tribal organization, you must complete the data "
        "sharing consent statement before submitting your audit."
    )
