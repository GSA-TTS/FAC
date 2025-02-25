import { checkValidity } from './validate.js';
import { queryAPI } from './api';

const FORM = document.forms[0];
var isUEIValidated = false;

function handleUEIDResponse({ valid, response, errors }) {
  if (valid) {
    handleValidUei(response);
  } else {
    handleInvalidUei(errors);
  }
}

function handleValidUei(response) {
  document.getElementById('auditee_name').value = response.auditee_name;
  populateModal('success', response.auditee_name);
}

function handleInvalidUei(errors) {
  if (Object.keys(errors).includes('auditee_uei')) {
    populateModal('not-found');
  }
}

function handleApiError(e) {
  populateModal('connection-error');
  console.error(e);
}

function hideUeiStuff() {
  const ueiFormGroup =
    document.getElementById('auditee_uei').parentNode.parentNode;
  const ueiExplanations = Array.from(
    document.querySelectorAll('.uei-explanation')
  );
  [...ueiExplanations, ueiFormGroup].forEach((node) =>
    node.setAttribute('hidden', 'hidden')
  );
}

function showValidUeiInfo() {
  const auditeeUei = document.getElementById('auditee_uei').value;
  const auditeeName = document.getElementById('auditee_name');
  const ueiInfoEl = document.createElement('div');

  let dl; let dtUei; let ddUei; let dtName; let ddName;
  dl = document.createElement('dl');
  dtUei = document.createElement('dt');
  ddUei = document.createElement('dd');
  dtName = document.createElement('dt');
  ddName = document.createElement('dd');

  dl.setAttribute('data-testid', 'uei-info');
  dtUei.textContent = 'Unique Entity ID';
  ddUei.textContent = auditeeUei;
  dtName.textContent = 'Auditee name';
  ddName.textContent = auditeeName.value;

  dl.append(dtUei,ddUei,dtName,ddName);
  ueiInfoEl.appendChild(dl);

  auditeeName.removeAttribute('disabled');
  auditeeName.parentNode.setAttribute('hidden', 'hidden');
  document.getElementById('valid-uei-info').replaceWith(ueiInfoEl);
}

function setupFormWithValidUei() {
  hideUeiStuff();
  showValidUeiInfo();
  isUEIValidated = true;
  setFormDisabled(false);
}

function resetModal() {
  const modalContainerEl = document.querySelector(
    '#uei-search-result .usa-modal__main'
  );
  const modalHeadingEl = modalContainerEl.querySelector('h2');
  const modalDescriptionEl = modalContainerEl.querySelector(
    '#uei-search-result-description'
  );
  const modalButtonPrimaryEl = modalContainerEl.querySelector('button.primary');
  const modalButtonSecondaryEl =
    modalContainerEl.querySelector('button.secondary');

  modalHeadingEl.textContent = '';
  modalDescriptionEl.innerHTML = '';
  modalButtonPrimaryEl.textContent = '';
  modalButtonSecondaryEl.textContent = '';

  document.querySelector('.uei-search-result').classList.add('loading');
}

// 'connection-error' | 'not-found' | 'success'
function populateModal(formStatus, auditeeName) {
  const auditeeUei = document.getElementById('auditee_uei').value;
  const modalContainerEl = document.querySelector(
    '#uei-search-result .usa-modal__main'
  );
  const modalHeadingEl = modalContainerEl.querySelector('h2');
  const modalDescriptionEl = modalContainerEl.querySelector(
    '#uei-search-result-description'
  );
  const modalButtonPrimaryEl = modalContainerEl.querySelector('button.primary');
  const modalButtonSecondaryEl =
    modalContainerEl.querySelector('button.secondary');

  const modalContent = {
    'connection-error': {
      heading: `We can't connect to SAM.gov to confirm your UEI.`,
      description: `
        <dl>
          <dt>UEI you entered</dt>
          <dd>${auditeeUei}</dd>
        </dl>
        <p>We can't proceed without confirming your UEI with SAM.gov. We’re sorry for the delay.</p>
        `,
      buttons: {
        primary: {
          text: `Go back`,
        },
      },
    },
    success: {
      heading: 'Search Result',
      description: `
        <dl>
          <dt>Unique Entity ID</dt>
          <dd>${auditeeUei}</dd>
          <dt>Auditee name</dt>
          <dd>${auditeeName}</dd>
        </dl>
        <p>Click continue to create a new audit submission for this auditee.</p>
        <p>Not the auditee you’re looking for? Go back, check the UEI you entered, and try again.</p>
      `,
      buttons: {
        primary: {
          text: `Continue`,
        },
        secondary: { text: `Go back` },
      },
    },
    'not-found': {
      heading: 'Your UEI is not recognized',
      description: `
        <dl>
          <dt>UEI you entered</dt>
          <dd>${auditeeUei}</dd>
        </dl>
        <p>We can't proceed without confirming that you have a valid UEI. We’re sorry for the delay.</p>
        <p>You can try re-entering the UEI. If you don’t have the UEI, you may find it at <a href="https://sam.gov">SAM.gov</a>.</p>
      `,
      buttons: {
        primary: {
          text: `Go back`,
        },
      },
    },
  };

  const contentForStatus = modalContent[formStatus];
  modalHeadingEl.textContent = contentForStatus.heading;
  modalDescriptionEl.innerHTML = contentForStatus.description;
  modalButtonPrimaryEl.textContent = contentForStatus.buttons.primary.text;

  if (contentForStatus.buttons.secondary) {
    modalButtonSecondaryEl.textContent =
      contentForStatus.buttons.secondary.text;
  }

  if (formStatus == 'success') {
    modalButtonPrimaryEl.onclick = setupFormWithValidUei;
  }

  document.querySelector('.uei-search-result').classList.remove('loading');
}

function validateUEID() {
  resetModal();

  const auditee_uei = document.getElementById('auditee_uei').value;

  queryAPI(
    '/api/sac/ueivalidation',
    { auditee_uei },
    {
      method: 'POST',
    },
    [handleUEIDResponse, handleApiError]
  );
}

function validateFyStartDate(fyInput) {
  if (fyInput.value == '') return;

  const fyFormGroup = document.querySelector('.usa-form-group.validate-fy');
  const fyErrorContainer = document.getElementById('fy-error-message');
  const userFy = {};
  [userFy.year, userFy.month, userFy.day] = fyInput.value.split('-');
  fyErrorContainer.innerHTML = '';

  if (userFy.year < 2016) {
    const errorEl = document.createElement('li');
    errorEl.innerHTML =
      'We are currently only accepting audits from FY16 or later.\
      To submit an audit for a different fiscal period, \
      visit the <a href="https://facides.census.gov/Account/Login.aspx">Census Bureau</a>.';
    fyErrorContainer.appendChild(errorEl);
    fyFormGroup.classList.add('usa-form-group--error');
    fyErrorContainer.focus();
  } else {
    fyFormGroup.classList.remove('usa-form-group--error');
  }

  setFormDisabled(!allResponsesValid());
}

function setFormDisabled(shouldDisable) {
  const continueBtn = document.getElementById('continue');
  // If we want to disable the button, do it.
  if (shouldDisable) {
    continueBtn.disabled = true;
    return;
  }

  // If we want to enable the button, the UEI validation should be done.
  if (!shouldDisable && isUEIValidated) {
    continueBtn.disabled = false;
  } else {
    continueBtn.disabled = true;
  }
}

function allResponsesValid() {
  const inputsWithErrors = document.querySelectorAll('[class *="--error"]');
  return inputsWithErrors.length == 0;
}

function performValidations(field) {
  const errors = checkValidity(field);
  setFormDisabled(errors.length > 0);
}

function attachEventHandlers() {
  const btnValidateUEI = document.getElementById('auditee_uei-btn');
  btnValidateUEI.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('auditee_uei').value = document
      .getElementById('auditee_uei')
      .value.toUpperCase();
    validateUEID();
  });

  FORM.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!allResponsesValid()) return;
    FORM.submit();
  });

  const fieldsNeedingValidation = Array.from(
    document.querySelectorAll('#check-eligibility input')
  );
  fieldsNeedingValidation.forEach((q) => {
    q.addEventListener('blur', (e) => {
      performValidations(e.target);
    });
  });

  const fyInput = document.getElementById('auditee_fiscal_period_start');
  fyInput.addEventListener('change', (e) => {
    validateFyStartDate(e.target);
  });
}
function attachDatePickerHandlers() {
  const dateInputsNeedingValidation = Array.from(
    document.querySelectorAll('.usa-date-picker__wrapper input[type=text]')
  );
  dateInputsNeedingValidation.forEach((q) => {
    q.addEventListener('blur', (e) => {
      performValidations(e.target);
    });
  });
}

function init() {
  attachEventHandlers();
  window.addEventListener('load', attachDatePickerHandlers, false); // Need to wait for date-picker text input to render.
  setFormDisabled(true); // Disabled initially, re-enables after filling everything out.
}

init();
