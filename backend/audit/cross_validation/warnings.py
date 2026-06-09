def warn_auditee_auditor_ein_match():
    return (
        "In the General Information form, the auditee EIN and auditor EIN are the same."
    )


def warn_name_fields_not_unique(duplicate_fields: list, shared_value: str):
    field_list = ", ".join(duplicate_fields)
    return (
        f"In the General Information form, the following name fields share the same value. "
        f'"{shared_value}" - {field_list}.'
    )
