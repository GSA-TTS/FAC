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

    if (!selectedAction) {
        if (requesterSection) requesterSection.hidden = true;
        if (materialSection) materialSection.hidden = true;
        if (nonMaterialSection) nonMaterialSection.hidden = true;
        if (auditOpinionChangesSection) {
            auditOpinionChangesSection.hidden = true;
        }
        return;
    }

    if (requesterSection) {
        requesterSection.hidden = false;
    }

    if (selectedAction.value === "audit_pdf") {
        if (materialSection) materialSection.hidden = false;
        if (nonMaterialSection) nonMaterialSection.hidden = true;

        if (auditOpinionChangesSection) {
            auditOpinionChangesSection.hidden = false;
        }
    } else if (selectedAction.value === "sfsac_only") {
        if (materialSection) materialSection.hidden = true;
        if (nonMaterialSection) nonMaterialSection.hidden = false;

        if (auditOpinionChangesSection) {
            auditOpinionChangesSection.hidden = true;
        }
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
