from audit.cross_validation.naming import (
    SECTION_NAMES,
    camel_to_snake,
    snake_to_camel,
)

at_root_sections = ("audit_information", "general_information")


def get_shaped_section(sac, section_name):
    """Extract either None or the appropriate dict from the section."""
    true_name = camel_to_snake(section_name) or section_name
    section = getattr(sac, true_name, None)
    if true_name in at_root_sections:
        return section

    if section:
        return section.get(snake_to_camel(true_name), {})

    return None


def sac_validation_shape(sac):
    """
    Takes an instance of SingleAuditChecklist and converts it to the shape
    expected by the validation functions.

    This function exists so that as either the SingleAuditChecklist or the
    validation shape changes we only have to make adjustments in one place.

    The sections that have spreadsheet workbooks all have root-level properties that
    are the camel-case names of those sections. This function eliminates these names
    and moves the actual values to the top level as part of returning a structure
    that's appropriate for passing to the validation functions.

    For example, if the Audit Information and Notes to SEFA sections have content,
    this function wil return something like:

    {
        "sf_sac_sections": {
            "audit_information": {
                "dollar_threshold": ...,
                "is_going_concern_included": ...,
                "is_internal_control_deficiency_disclosed": ...,
                "is_internal_control_material_weakness_disclosed": ...,
                "is_material_noncompliance_disclosed": ...,
                "is_aicpa_audit_guide_included": ...,
                "is_low_risk_auditee": ...,
                [other audit_information fields]
            },
            "notes_to_sefa": {
                "auditee_uei": ...,
                "accounting_policies": ...,
                "is_minimis_rate_used": ...,
                "rate_explained": ...,
                "notes_to_sefa_entries": ...,
                [other notes_to_sefa fields]

            },
            "federal_awards": None,
            ...
        },
        "sf_sac_meta": { ... },
    }

    """

    shape = {
        "sf_sac_sections": {k: get_shaped_section(sac, k) for k in SECTION_NAMES},
        "sf_sac_meta": {
            "submitted_by": sac.submitted_by,
            "date_created": sac.date_created,
            "submission_status": sac.submission_status,
            "report_id": sac.report_id,
            "audit_type": sac.audit_type,
            "transition_name": sac.transition_name,
            "transition_date": sac.transition_date,
        },
    }
    return shape
