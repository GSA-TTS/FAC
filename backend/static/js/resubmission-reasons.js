function setSectionVisibility(section, visible) {
    if (!section) {
        return;
    }

    section.hidden = !visible;

    section.querySelectorAll("input, textarea, select").forEach((field) => {
        field.disabled = !visible;
    });
}

function toggleReasonSections() {
    const selectedAction = document.querySelector(
        'input[name="resubmission_action"]:checked'
    );

    const requesterSection = document.getElementById("requester-section");
    const materialSection = document.getElementById("material-change-section");
    const nonMaterialSection = document.getElementById(
        "non-material-change-section"
    );
    const sfsacOnlySection = document.getElementById(
        "sfsac-only-change-section"
    );
    const auditOpinionChangesSection = document.getElementById(
        "audit-opinion-changes-section"
    );
    const auditOpinionChangesHint = document.getElementById(
        "audit-opinion-changes-hint"
    );

    // Reset conditional sections.
    setSectionVisibility(requesterSection, Boolean(selectedAction));
    setSectionVisibility(materialSection, false);
    setSectionVisibility(nonMaterialSection, false);
    setSectionVisibility(sfsacOnlySection, false);
    setSectionVisibility(auditOpinionChangesSection, false);

    if (!selectedAction) {
        return;
    }

    if (selectedAction.value === "audit_pdf") {
        setSectionVisibility(materialSection, true);
        setSectionVisibility(auditOpinionChangesSection, true);

        if (auditOpinionChangesHint) {
            auditOpinionChangesHint.textContent = "This field is required.";
        }
    } else if (selectedAction.value === "non_material_pdf") {
        setSectionVisibility(nonMaterialSection, true);
        setSectionVisibility(auditOpinionChangesSection, true);

        if (auditOpinionChangesHint) {
            auditOpinionChangesHint.textContent = "This field is optional.";
        }
    } else if (selectedAction.value === "sfsac_only") {
        setSectionVisibility(sfsacOnlySection, true);
    }
}

// Populate the correct sections when the page first loads.
document.addEventListener("DOMContentLoaded", toggleReasonSections);

// Handle future radio changes, including on the edit page.
document.addEventListener("change", (event) => {
    if (event.target.matches('input[name="resubmission_action"]')) {
        toggleReasonSections();
    }
});
