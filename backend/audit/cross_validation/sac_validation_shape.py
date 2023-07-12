def sac_validation_shape(sac):
    """
    Takes an instance of SingleAuditChecklist and converts it to the shape
    expected by the validation functions.

    This function exists so that as either the SingleAuditChecklist or the
    validation shape changes we only have to make adjustments in one place.
    """
    shape = {
        "sf_sac_sections": {
            "general_information": sac.general_information,
            "federal_awards": sac.federal_awards,
            "corrective_action_plan": sac.corrective_action_plan,
            "findings_text": sac.findings_text,
            "findings_uniform_guidance": sac.findings_uniform_guidance,
            "additional_ueis": sac.additional_ueis,
        },
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
