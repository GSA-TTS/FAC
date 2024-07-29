from .errors import err_total_amount_expended
from config.settings import DOLLAR_THRESHOLD


def check_total_amount_expended(sac_dict, *_args, **_kwargs):
    """
    Check that the total amount expended is less than the dollar threshold
    """
    all_sections = sac_dict["sf_sac_sections"]

    federal_awards = all_sections.get("federal_awards", {})

    if not (federal_awards):
        return []

    total_amount_expended = federal_awards.get("total_amount_expended")

    if total_amount_expended < DOLLAR_THRESHOLD:
        return [{"error": err_total_amount_expended(total_amount_expended)}]
    else:
        return []
