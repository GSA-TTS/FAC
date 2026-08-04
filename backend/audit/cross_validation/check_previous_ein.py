from audit.utils import Util


def check_previous_ein(sac, sar=None):
    """
    Warn when the EIN for a new submission does not match the EIN
    from the previous fully accepted dissemination record with the same UEI.
    """
    general_information = sac["sf_sac_sections"].get(
        "general_information",
        {},
    )

    current_uei = general_information.get("auditee_uei")
    current_ein = general_information.get("ein")

    warning = Util.get_previous_ein_warning(
        current_uei,
        current_ein,
    )

    if not warning:
        return []

    return [{"warning": warning}]
