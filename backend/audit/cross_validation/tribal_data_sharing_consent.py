from .errors import (
    err_missing_tribal_data_sharing_consent,
    err_unexpected_tribal_data_sharing_consent,
)


def tribal_data_sharing_consent(sac_dict, *_args, **_kwargs):
    """
    Checks that if the user identified as a tribal organization
    then there must be a completed data sharing consent form associated with the submission
    """
    all_sections = sac_dict["sf_sac_sections"]
    organization_type = all_sections["general_information"].get(
        "user_provided_organization_type"
    )

    required_fields = (
        "tribal_authorization_certifying_official_title",
        "is_tribal_information_authorized_to_be_public",
        "tribal_authorization_certifying_official_name",
    )
    must_be_truthy_fields = (
        "tribal_authorization_certifying_official_title",
        "tribal_authorization_certifying_official_name",
    )
    if organization_type == "tribal":
        if not (tribal_data_consent := all_sections.get("tribal_data_consent")):
            return [{"error": err_missing_tribal_data_sharing_consent()}]

        # this should check for consent form completeness once form data structure is finalized
        for rfield in required_fields:
            if rfield not in tribal_data_consent:
                return [{"error": err_missing_tribal_data_sharing_consent()}]
        for tfield in must_be_truthy_fields:
            if not tribal_data_consent.get(tfield):
                return [{"error": err_missing_tribal_data_sharing_consent()}]
        if not tribal_data_consent.get(
            "is_tribal_information_authorized_to_be_public"
        ) in (True, False):
            return [{"error": err_missing_tribal_data_sharing_consent()}]

    # this shouldn't be possible now, but may be in the future
    elif tc := all_sections.get("tribal_data_consent"):
        if tc.get("is_tribal_information_authorized_to_be_public"):
            return [{"error": err_unexpected_tribal_data_sharing_consent()}]
    return []
