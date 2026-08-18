function toggleReasonSections() {
    const selectedAction = document.querySelector(
        'input[name="resubmission_action"]:checked'
    );

    const requesterSection = document.getElementById("requester-section");
    const materialSection = document.getElementById("material-change-section");
    const nonMaterialSection = document.getElementById(
        "non-material-change-section"
    );
    const auditOpinionChangesSection = document.getElementById(
        "audit-opinion-changes-section"
    );

    if (requesterSection) requesterSection.hidden = !selectedAction;
    if (materialSection) materialSection.hidden = true;
    if (nonMaterialSection) nonMaterialSection.hidden = true;
    if (auditOpinionChangesSection) {
        auditOpinionChangesSection.hidden = true;
    }

    if (!selectedAction) {
        return;
    }

    if (selectedAction.value === "audit_pdf") {
        if (materialSection) materialSection.hidden = false;
        if (auditOpinionChangesSection) {
            auditOpinionChangesSection.hidden = false;
        }
    } else if (selectedAction.value === "non_material_pdf") {
        if (nonMaterialSection) nonMaterialSection.hidden = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document
        .querySelectorAll('input[name="resubmission_action"]')
        .forEach((radio) => {
            radio.addEventListener("change", toggleReasonSections);
        });

    toggleReasonSections();
});
