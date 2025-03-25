import logging

from audit.cross_validation.naming import NC, SECTION_NAMES

at_root_sections = (NC.AUDIT_INFORMATION, NC.GENERAL_INFORMATION, NC.TRIBAL_DATA_CONSENT)  # type: ignore

logger = logging.getLogger(__name__)


def audit_validation_shape(audit):
    """
    Takes an instance of Audit and converts it to the shape
    expected by the validation functions.

    This function exists so that as either the Audit or the
    validation shape changes we only have to make adjustments in one place.

    The sections that have spreadsheet workbooks all have root-level properties that
    are the camel-case names of those sections. This function eliminates these names
    and moves the actual values to the top level as part of returning a structure
    that's appropriate for passing to the validation functions.

    For example, if the Audit Information and Notes to SEFA sections have content,
    this function will return something like:

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
        "waiver_types": [ ... ],
    }

    """
    from audit.models import Access, SacValidationWaiver

    shape = {
        "sf_sac_sections": {k: get_shaped_section(audit, k) for k in SECTION_NAMES},
        "sf_sac_meta": {
            "submitted_by": audit.submitted_by,
            "date_created": audit.created_at,
            "submission_status": audit.submission_status,
            "report_id": audit.report_id,
            "audit_type": audit.audit_type,
            "data_source": audit.data_source,
        },
    }

    # Querying the SacValidationWaiver table for waivers
    waivers = SacValidationWaiver.objects.filter(report_id=audit.report_id)

    # Extracting waiver types from waivers
    waiver_types = [
        waiver_type for waiver in waivers for waiver_type in waiver.waiver_types
    ]

    shape["waiver_types"] = waiver_types

    certifying_auditee = Access.objects.filter(
        audit=audit, role="certifying_auditee_contact"
    ).first()

    certifying_auditor = Access.objects.filter(
        audit=audit, role="certifying_auditor_contact"
    ).first()

    if certifying_auditee:
        shape["sf_sac_meta"].update(
            {"certifying_auditee_contact": certifying_auditee.email}
        )

    if certifying_auditor:
        shape["sf_sac_meta"].update(
            {"certifying_auditor_contact": certifying_auditor.email}
        )

    return shape


def get_shaped_section(audit, section_name):
    audit_translation = SECTION_NAMES.get(section_name).audit_translation

    return (
        audit_translation(audit)
        if audit_translation
        else audit.audit.get(section_name, None)
    )
