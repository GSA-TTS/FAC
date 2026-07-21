from audit.models.constants import RESUBMISSION_ACTION


def check_resubmission_metadata(data, sar=None):
    sf_sac_meta = data.get("sf_sac_meta", {})
    resubmission_meta = sf_sac_meta.get("resubmission_meta") or {}

    if not resubmission_meta.get("previous_report_id"):
        return []

    errors = []

    action = resubmission_meta.get("resubmission_action")
    requester = resubmission_meta.get("resubmission_requester")
    material = resubmission_meta.get("material_change_reasons")
    non_material = resubmission_meta.get("non_material_change_reasons")

    if not action:
        errors.append({"error": "Resubmission type is required."})

    if not requester:
        errors.append({"error": "At least one resubmission requester is required."})

    if action == RESUBMISSION_ACTION.AUDIT_PDF and not material:
        errors.append(
            {
                "error": (
                    "At least one material change is required for an "
                    "audit PDF resubmission."
                )
            }
        )

    if action == RESUBMISSION_ACTION.SFSAC_ONLY and not non_material:
        errors.append(
            {
                "error": (
                    "At least one non-material change is required for an "
                    "SF-SAC-only modification."
                )
            }
        )

    return errors
