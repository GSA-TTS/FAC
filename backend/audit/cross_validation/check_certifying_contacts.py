from .errors import (
    err_certifying_contacts_should_not_match,
)


def check_certifying_contacts(sac_dict, *_args, **_kwargs):
    """
    Check that the certifying auditor and auditee do not have the same email address.
    """

    sf_sac_meta = sac_dict.get("sf_sac_meta", {})
    certifying_auditee_contact = sf_sac_meta.get("certifying_auditee_contact")
    certifying_auditor_contact = sf_sac_meta.get("certifying_auditor_contact")
    errors = []

    if certifying_auditee_contact and certifying_auditor_contact:
        if certifying_auditee_contact == certifying_auditor_contact:
            errors.append({"error": err_certifying_contacts_should_not_match()})

    return errors
