function toggleReasonSections() {
    const selectedAction = document.querySelector(
        'input[name="resubmission_action"]:checked'
    );

    const requesterSection = document.getElementById("requester-section");
    const materialSection = document.getElementById("material-change-section");
    const nonMaterialSection = document.getElementById("non-material-change-section");

    if (!requesterSection || !materialSection || !nonMaterialSection) {
        return;
    }

    if (!selectedAction) {
        requesterSection.hidden = true;
        materialSection.hidden = true;
        nonMaterialSection.hidden = true;
        return;
    }

    // Always show requester after a radio is selected
    requesterSection.hidden = false;

    if (selectedAction.value === "audit_pdf") {
        materialSection.hidden = false;
        nonMaterialSection.hidden = true;
    } else if (selectedAction.value === "sfsac_only") {
        materialSection.hidden = true;
        nonMaterialSection.hidden = false;
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
