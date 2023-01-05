import { checkValidity } from './validate.js';

const URL = './report_submission/auditeeinfo/';
const nextStep = './report_submission/accessandsubmission';
const FORM = document.forms[0];
/*
function submitForm() {
  const formData = serializeFormData(new FormData(FORM));
  formData.auditee_fiscal_period_start = new Date(
    formData.auditee_fiscal_period_start
  ).toLocaleDateString('en-CA');
  formData.auditee_fiscal_period_end = new Date(
    formData.auditee_fiscal_period_end
  ).toLocaleDateString('en-CA');

  queryAPI(
    ENDPOINT,
    formData,
    {
      method: 'POST',
    },
    [handleAuditeeResponse, handleErrorResponse]
  );
}
*/ 
function handleAuditeeResponse(data) {
  console.log(data);
  if (data.next == '/sac/accessandsubmission') {
    const nextUrl = '../step-3/';
    window.location.href = nextUrl;
  } else {
    console.log(data.errors);
  }
}
function handleErrorResponse() {
  console.log('ERROR: Form submission error.');
}

function handleUEIDResponse({ valid, response, errors }) {
  if (valid) {
    handleValidUei(response);
  } else {
    handleInvalidUei(errors);
  }
}

function handleValidUei({ auditee_name }) {
  document.getElementById('auditee_name').value = auditee_name;
  populateModal('success', auditee_name);
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

function proceedWithoutUei() {
  const nameInputEl = document.getElementById('auditee_name');
  const requiredStar = document.createElement('abbr');

  requiredStar.setAttribute('title', 'required');
  requiredStar.setAttribute('class', 'usa-hint usa-hint--required');
  requiredStar.textContent = '*';

  nameInputEl.removeAttribute('disabled');
  nameInputEl.setAttribute('required', 'true');
  document.querySelector('[for=auditee_name]').appendChild(requiredStar);
  document.getElementById('no-uei-warning').hidden = false;

  hideUeiStuff();
}

function hideUeiStuff() {
  const ueiFormGroup =
    document.getElementById('auditee_uei').parentNode.parentNode;
  const ueiExplanations = Array.from(
    document.querySelectorAll('.uei-explanation')
  );
  [...ueiExplanations, ueiFormGroup].forEach((node) =>
    node.setAttribute('hidden', 'true')
  );
}

function showValidUeiInfo() {
  const auditeeUei = document.getElementById('auditee_uei').value;
  const auditeeName = document.getElementById('auditee_name').value;
  const ueiInfoEl = document.createElement('div');

  ueiInfoEl.innerHTML = `
    <dl data-testid="uei-info">
      <dt>Unique Entity ID</dt>
      <dd>${auditeeUei}</dd>
      <dt>Auditee name</dt>
      <dd>${auditeeName}</dd>
    </dl>
  `;

  document
    .getElementById('auditee_name')
    .parentNode.setAttribute('hidden', 'true');
  document.getElementById('no-uei-warning').replaceWith(ueiInfoEl);
}

function setupFormWithValidUei() {
  hideUeiStuff();
  showValidUeiInfo();
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
        <p>We’re sorry for the delay. You can continue, but we’ll need confirm your UEI before your audit submission can be certified.</p>
        <p>You might also want to check the UEI you entered, go back, and try again.</p>
        `,
      buttons: {
        primary: {
          text: `Go back`,
        },
        secondary: {
          text: `Continue without a confirmed UEI`,
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
        <p>You can try re-entering the UEI. If you don’t have the UEI, you may find it at <a href="https://sam.gov">SAM.gov</a>.</p>
        <p>You may also continue without the UEI, and you will be prompted to update the UEI before you can submit your audit.</p>
      `,
      buttons: {
        primary: {
          text: `Continue`,
        },
        secondary: { text: `Go back` },
      },
    },
  };

  const contentForStatus = modalContent[formStatus];
  modalHeadingEl.textContent = contentForStatus.heading;
  modalDescriptionEl.innerHTML = contentForStatus.description;
  modalButtonPrimaryEl.textContent = contentForStatus.buttons.primary.text;
  modalButtonSecondaryEl.textContent = contentForStatus.buttons.secondary.text;

  if (formStatus == 'success') {
    modalButtonPrimaryEl.onclick = setupFormWithValidUei;
  }

  if (formStatus == 'not-found') {
    modalButtonPrimaryEl.onclick = proceedWithoutUei;
  }

  if (formStatus == 'connection-error') {
    modalButtonSecondaryEl.onclick = proceedWithoutUei;
  }

  document.querySelector('.uei-search-result').classList.remove('loading');
}

function validateUEID() {
  resetModal();

  const auditee_uei = document.getElementById('auditee_uei').value;
  const headers = new Headers();
  headers.append('Content-type', 'application/json');
  fetch('/api/sac/ueivalidation', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({ auditee_uei}),
  })
    .then((resp) => resp.json())
    .then((data) => handleUEIDResponse(data))
    .catch((e) => handleApiError(e));
/*
  queryAPI(
    '/sac/ueivalidation',
    { auditee_uei },
    {
      method: 'POST',
    },
    [handleUEIDResponse, handleApiError]
  );
*/
}

function validateFyStartDate(fyInput) {
  if (fyInput.value == '') return;

  const fyFormGroup = document.querySelector('.usa-form-group.validate-fy');
  const fyErrorContainer = document.getElementById('fy-error-message');
  const userFy = {};
  [userFy.year, userFy.month, userFy.day] = fyInput.value.split('-');
  fyErrorContainer.innerHTML = '';

  if (userFy.year < 2020) {
    const errorEl = document.createElement('li');
    errorEl.innerHTML =
      'We are currently only accepting audits from FY22.\
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

function serializeFormData(formData) {
  return Object.fromEntries(formData);
}

function setFormDisabled(shouldDisable) {
  const continueBtn = document.getElementById('continue');
  continueBtn.disabled = shouldDisable;
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
    validateUEID();
  });

  FORM.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!allResponsesValid()) return;
    submitForm();
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
}

init();
