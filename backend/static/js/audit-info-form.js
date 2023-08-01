/*
  HTML5 doesn't provide a native way to set multiple choice options as required, without setting ALL of them as required. 
  This solution sets them all as required, so a user is notified if they try to submit without selecting an answer.
  If they select an answer, the options are set to no longer be required. 
  This function attaches handles by the name of the <input> tag, which is shared between choices. 
*/
function setCheckboxRequired(name) {
  let checkboxes = document.getElementsByName(name);

  // First make sure the required tag is set properly on all elements
  for (var i = 0; i < checkboxes.length; i++) {
    let elements = document.getElementsByName(name);
    var someChecked = false;
    elements.forEach(
      (element) => (someChecked = someChecked || element.checked)
    );
    elements.forEach((element) => (element.required = !someChecked));
  }

  // Attach the event handler that will change the required tag when a user selects (or unselects) an option
  for (var j = 0; j < checkboxes.length; j++) {
    checkboxes[j].addEventListener('input', () => {
      let elements = document.getElementsByName(name);
      var someChecked = false;
      elements.forEach(
        (element) => (someChecked = someChecked || element.checked)
      );
      elements.forEach((element) => (element.required = !someChecked));
    });
  }
}

function init() {
  setCheckboxRequired('GGAP_results');
  setCheckboxRequired('going_concern_included');
  setCheckboxRequired('internal_control_deficiency_disclosed');
  setCheckboxRequired('internal_control_material_weakness_disclosed');
  setCheckboxRequired('material_noncompliance_disclosed');
  setCheckboxRequired('AICPA_audit_guide_included');
  setCheckboxRequired('low_risk_auditee');
}

init();
