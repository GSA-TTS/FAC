const FORM = document.getElementById('upload-report__form');
const not_gaap_id = 'gaap_results--not_gaap';
const sp_framework_div = document.querySelector('#sp_framework_section');

/*
  HTML5 doesn't provide a native way to set multiple choice options as required, without setting ALL of them as required. 
  This solution sets them all as required, so a user is notified if they try to submit without selecting an answer.
  If they select an answer, the options are set to no longer be required. 
  This function attaches handles by the name of the <input> tag, which is shared between choices. 
*/
function setCheckboxRequired(name) {
  let checkboxes = document.getElementsByName(name);
  // First make sure the required tag is set properly on all elements
  for (let i = 0; i < checkboxes.length; i++) {
    let elements = document.getElementsByName(name);
    let someChecked = false;
    elements.forEach((element) => {
      someChecked = someChecked || element.checked;
      if (element.id === not_gaap_id) toggle_sp_div();
    });
    elements.forEach((element) => (element.required = !someChecked));
  }

  // Attach the event handler that will change the required tag when a user selects (or unselects) an option
  for (let j = 0; j < checkboxes.length; j++) {
    checkboxes[j].addEventListener('input', () => {
      let elements = document.getElementsByName(name);
      let someChecked = false;
      elements.forEach((element) => {
        someChecked = someChecked || element.checked;
        if (element.id === not_gaap_id) toggle_sp_div();
      });
      elements.forEach((element) => (element.required = !someChecked));
    });
  }
}

function attachEventHandlers() {
  /* Uncheck sp_ fields if they are not applicable */
  FORM.addEventListener('submit', (e) => {
    e.preventDefault();
    const not_gaap_cb = document.querySelector(`#${not_gaap_id}`);
    if (!not_gaap_cb.checked) {
      const basis = document.querySelectorAll(
        'input[name="sp_framework_basis"]'
      );
      basis.forEach((basi) => {
        basi.checked = false;
      });
      const reqds = document.querySelectorAll(
        'input[name="is_sp_framework_required"]'
      );
      reqds.forEach((reqd) => {
        reqd.checked = false;
      });
      const opinions = document.querySelectorAll(
        'input[name="sp_framework_opinions"]'
      );
      opinions.forEach((opinion) => {
        opinion.checked = false;
      });
    }
    FORM.submit();
  });
}

function init() {
  setCheckboxRequired('gaap_results');
  setCheckboxRequired('sp_framework_basis');
  setCheckboxRequired('is_sp_framework_required');
  setCheckboxRequired('sp_framework_opinions');
  setCheckboxRequired('is_going_concern_included');
  setCheckboxRequired('is_internal_control_deficiency_disclosed');
  setCheckboxRequired('is_internal_control_material_weakness_disclosed');
  setCheckboxRequired('is_material_noncompliance_disclosed');
  setCheckboxRequired('is_aicpa_audit_guide_included');
  setCheckboxRequired('is_low_risk_auditee');
  attachEventHandlers();
}

/* show or hide sp_f fields based on no_gaap being checked */
function toggle_sp_div() {
  const not_gaap_cb = document.querySelector(`#${not_gaap_id}`);
  console.log('toggle', not_gaap_cb.checked);
  if (not_gaap_cb.checked) {
    sp_framework_div.removeAttribute('hidden');
  } else {
    sp_framework_div.setAttribute('hidden', true);
  }
}

window.onload = init;
