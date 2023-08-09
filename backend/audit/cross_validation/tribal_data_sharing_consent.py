from .errors import err_missing_tribal_data_sharing_consent


def tribal_data_sharing_consent(sac_dict):
    """
    Checks that if the user identified as a tribal organization
    then there must be a completed data sharing consent form associated with the submission
    """
    all_sections = sac_dict["sf_sac_sections"]
    organization_type = all_sections["general_information"].get(
        "user_provided_organization_type"
    )

    if organization_type == "tribal":
        if not (tribal_data_consent := all_sections.get("tribal_data_consent")):
            return [{"error": err_missing_tribal_data_sharing_consent()}]

        # this should check for consent form completeness once form data structure is finalized
        if not tribal_data_consent:
            return [{"error": err_missing_tribal_data_sharing_consent()}]

    return []
