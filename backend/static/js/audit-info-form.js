const not_gaap_id = 'gaap_results--not_gaap';
const sp_framework_div = document.querySelector('#sp_framework_section');
const form = document.getElementById('upload-report__form');

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
  // The checkboxes for the three optional questions
  const basis = document.getElementsByName('sp_framework_basis');
  const not_gaap_cb = document.getElementsByName('is_sp_framework_required');
  const opinions = document.getElementsByName('sp_framework_opinions');

  // Add event listener to the "Not GAAP" option of question one
  // (a) Set the div to be hidden or not depending on if the box is checked
  // (b) Set required on each sub-question based on if the box is checked or not
  const checkbox_not_gaap = document.getElementById('gaap_results--not_gaap');
  checkbox_not_gaap.addEventListener('click', () => {
    sp_framework_div.hidden = !checkbox_not_gaap.checked;

    basis.forEach((checkbox) => {
      checkbox.required = checkbox_not_gaap.checked;
    });
    not_gaap_cb.forEach((checkbox) => {
      checkbox.required = checkbox_not_gaap.checked;
    });
    opinions.forEach((checkbox) => {
      checkbox.required = checkbox_not_gaap.checked;
    });
  });

  // For the subquestions, they need to be required/unrequired if one option is clicked.
  // i.e. if the subquestions are showing and an option is clicked, the question is no longer required.
  // These are overwritten to be not required if the "Not GAAP" checkbox is un-checked.
  basis.forEach((checkbox) => {
    // If any checkbox in basis is clicked, unrequire the section.
    checkbox.addEventListener('click', () => {
      basis.forEach((subbox) => {
        subbox.required = !checkbox.checked;
      });
    });
  });
  not_gaap_cb.forEach((checkbox) => {
    checkbox.addEventListener('click', () => {
      // If any checkbox in not_gaap_cb is clicked, unrequire the section.
      not_gaap_cb.forEach((subbox) => {
        subbox.required = !checkbox.checked;
      });
    });
  });
  opinions.forEach((checkbox) => {
    checkbox.addEventListener('click', () => {
      // If any checkbox in opinions is clicked, unrequire the section.
      opinions.forEach((subbox) => {
        subbox.required = !checkbox.checked;
      });
    });
  });

  // Add event listener to the larger form
  // If the "Not GAAP" option of quesion one is not checked, banish the optional questions.
  // So, if the user fills out optional questions then unchecks the "Not GAAP" option, they will not be submitted.
  form.addEventListener('submit', (e) => {
    const formData = new FormData(form);
    if (!checkbox_not_gaap.checked) {
      for (const test of [
        'is_sp_framework_required',
        'sp_framework_basis',
        'sp_framework_opinions',
      ]) {
        formData.delete(test);
      }
    }
    for (item of formData.entries()){
      console.log(item)
    }
  });
}

function init() {
  setCheckboxRequired('gaap_results');
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
  if (not_gaap_cb.checked) {
    sp_framework_div.removeAttribute('hidden');
  } else {
    sp_framework_div.setAttribute('hidden', true);
  }
}

window.onload = init;
