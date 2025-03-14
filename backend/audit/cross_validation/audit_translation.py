def translate_additional_ueis(audit):
    additional_ueis = audit.audit.get("additional_ueis", [])
    return (
        {
            "auditee_uei": audit.auditee_uei,
            "additional_ueis_entries": [
                {"additional_uei": uei} for uei in additional_ueis
            ],
        }
        if additional_ueis
        else None
    )


def translate_additional_eins(audit):
    additional_ueis = audit.audit.get("additional_eins", [])
    return (
        {
            "auditee_uei": audit.auditee_uei,
            "additional_eins_entries": [
                {"additional_ein": uei} for uei in additional_ueis
            ],
        }
        if additional_ueis
        else None
    )


def translate_cap(audit):
    cap_entries = audit.audit.get("corrective_action_plan", [])
    return (
        {
            "auditee_uei": audit.auditee_uei,
            "corrective_action_plan_entries": cap_entries,
        }
        if cap_entries
        else None
    )


def translate_federal_awards(audit):
    federal_awards = audit.audit.get("federal_awards", {})
    return (
        {
            "auditee_uei": audit.auditee_uei,
            "federal_awards": federal_awards.get("awards", []),
            "total_amount_expended": federal_awards.get("total_amount_expended", None),
        }
        if federal_awards
        else None
    )


def translate_findings_text(audit):
    findings_text = audit.audit.get("findings_text", [])
    return (
        {"auditee_uei": audit.auditee_uei, "findings_text_entries": findings_text}
        if findings_text
        else None
    )


def translate_findings_uniform_guidance(audit):
    guidance_entries = audit.audit.get("findings_uniform_guidance", [])
    return (
        {
            "auditee_uei": audit.auditee_uei,
            "findings_uniform_guidance_entries": guidance_entries,
        }
        if guidance_entries
        else None
    )


def translate_secondary_auditors(audit):
    secondary_auditors = audit.audit.get("secondary_auditors", [])
    return (
        {
            "auditee_uei": audit.auditee_uei,
            "secondary_auditors_entries": secondary_auditors,
        }
        if secondary_auditors
        else None
    )


def translate_notes_to_sefa(audit):
    return (
        {"auditee_uei": audit.auditee_uei, **audit.audit.get("notes_to_sefa", {})}
        if audit.audit.get("notes_to_sefa")
        else None
    )
