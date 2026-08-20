from audit.cross_validation.errors import (
    err_material_change_required,
    err_non_material_change_required,
    err_resubmission_requester_required,
    err_resubmission_type_required,
)

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
    sfsac_only = resubmission_meta.get("sfsac_only_change_reasons")

    if not action:
        errors.append({"error": err_resubmission_type_required()})

    if not requester:
        errors.append({"error": err_resubmission_requester_required()})

    if action == RESUBMISSION_ACTION.AUDIT_PDF and not material:
        errors.append({"error": err_material_change_required()})

    if action == RESUBMISSION_ACTION.NON_MATERIAL_PDF and not non_material:
        errors.append({"error": err_non_material_change_required()})

    if action == RESUBMISSION_ACTION.SFSAC_ONLY and not sfsac_only:
        errors.append({"error": err_non_material_change_required()})

    return errors
