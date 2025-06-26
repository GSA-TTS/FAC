from .errors import err_ein_attestation


def check_ein_attestations(sac_dict, *_args, **_kwargs):
    """
    Checks that the "EIN not an SSN" attestations are checked.
    """
    all_sections = sac_dict["sf_sac_sections"]
    auditee_ein_attestation = all_sections["general_information"].get("ein_not_an_ssn_attestation")
    auditor_ein_attestation = all_sections["general_information"].get("auditor_ein_not_an_ssn_attestation")
    
    errors = []
    if not auditee_ein_attestation:
            errors.append({"error": err_ein_attestation("ein_not_an_ssn_attestation")})
    if not auditor_ein_attestation:
            errors.append({"error": err_ein_attestation("auditor_ein_not_an_ssn_attestation")})

    return errors
