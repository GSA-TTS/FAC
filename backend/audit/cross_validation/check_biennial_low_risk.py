from .errors import err_biennial_low_risk


def check_biennial_low_risk(sac_dict, *_args, **_kwargs):
    """
    Check that both biennial and low risk flags aren't both set.
    """
    all_sections = sac_dict["sf_sac_sections"]

    general_information = all_sections.get("general_information", {})
    audit_information = all_sections.get("audit_information", {})

    if not (general_information and audit_information):
        return []

    audit_period_covered = general_information.get("audit_period_covered")
    is_low_risk_auditee = audit_information.get("is_low_risk_auditee")

    if audit_period_covered == "biennial" and is_low_risk_auditee:
        return [{"error": err_biennial_low_risk()}]
    else:
        return []
