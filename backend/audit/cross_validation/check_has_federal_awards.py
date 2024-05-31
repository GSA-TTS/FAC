from .errors import err_no_federal_awards


def check_has_federal_awards(sac_dict, *_args, **_kwargs):
    """
    Check that the submission contains at least one federal awards
    """

    all_sections = sac_dict.get("sf_sac_sections", {})
    federal_awards_section = all_sections.get("federal_awards") or {}
    federal_awards = federal_awards_section.get("federal_awards", [])

    errors = []
    if len(federal_awards) == 0:
        errors.append({"error": err_no_federal_awards()})

    return errors
