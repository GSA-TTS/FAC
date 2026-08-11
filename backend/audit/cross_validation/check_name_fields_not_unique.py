from collections import defaultdict

from .warnings import warn_name_fields_not_unique

NAME_FIELDS = {
    "auditee_name": "Auditee Name",
    "auditee_contact_name": "Auditee Contact Name",
    "auditor_contact_name": "Auditor Contact Name",
    "auditor_firm_name": "Auditor Firm Name",
}


def check_name_fields_not_unique(sac_dict, *_args, **_kwargs):
    """
    Warns if any of the simple name fields are identical.

    If a field is absent or None, it is skipped. The "required fields" individual check will get those.
    """
    all_sections = sac_dict["sf_sac_sections"]
    general_information = all_sections.get("general_information", {})

    present = {
        field: general_information[field]
        for field in NAME_FIELDS
        if general_information.get(field)
    }

    # Group fields by their shared value; each group with >1 field is a duplicate set.
    groups = defaultdict(list)
    for field, value in present.items():
        groups[value].append(field)

    # Emit one warning per duplicate set, with friendly names.
    warnings = []
    for shared_value, fields in groups.items():
        if len(fields) > 1:
            ordered = [NAME_FIELDS[f] for f in NAME_FIELDS if f in fields]
            warnings.append(
                {"warning": warn_name_fields_not_unique(ordered, shared_value)}
            )

    return warnings
