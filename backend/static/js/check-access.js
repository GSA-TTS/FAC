import { checkValidity } from './validate';
import { queryAPI } from './api';

const SUBMISSION_URL = '/report_submission/accessandsubmission/';
const NEXT_URL = '../../audit/';
const FORM = document.forms[0];
let addedContactNum = 1; // Counter for added contacts

function submitForm() {
  const formData = serializeFormData(new FormData(FORM));

  let preparedData = {};
  preparedData['certifying_auditee_contact'] =
    formData.auditee_certifying_official_email;
  preparedData['certifying_auditor_contact'] =
    formData.auditor_certifying_official_email;
  preparedData['auditee_contacts'] = contactsToArray(
    formData,
    'auditee_contacts_email'
  );
  preparedData['auditor_contacts'] = contactsToArray(
    formData,
    'auditor_contacts_email'
  );

  queryAPI(
    SUBMISSION_URL,
    preparedData,
    {
      method: 'POST',
    },
    [handleAccessResponse, handleErrorResponse]
  );
}

function handleAccessResponse(data) {
  if (data.report_id) {
    const nextUrlWithID = NEXT_URL + `${data.report_id}`;
    window.location.href = NEXT_URL;
  } else {
    console.log(data);
  }
}
function handleErrorResponse(e) {
  console.log('ERROR: Form submission error. ' + e);
  window.location.href = NEXT_URL;
}

function serializeFormData(formData) {
  return Object.fromEntries(formData);
}

function contactsToArray(formData, keyContains) {
  const regex = new RegExp(keyContains);
  let outputArray = [];
  for (var key in formData) {
    if (Object.hasOwn(formData, key)) {
      if (regex.test(key)) {
        outputArray.push(formData[key]);
      }
    }
  }
  return outputArray;
}

function setFormDisabled(shouldDisable) {
  const continueBtn = document.getElementById('create');
  continueBtn.disabled = shouldDisable;
}

function allResponsesValid() {
  const inputsWithErrors = document.querySelectorAll('[class *="--error"]');
  return inputsWithErrors.length === 0;
}

function performValidations(field) {
  const errors = checkValidity(field);
  setFormDisabled(errors.length > 0);
}

function appendContactField(btnEl) {
  const inputContainer = btnEl.parentElement;
  const template = inputContainer.querySelector('template');
  const newRow = template.content.cloneNode(true);

  const newInputs = newRow.querySelectorAll('input');
  newInputs.forEach(function (input) {
    input.id = input.id + '-' + addedContactNum;
    input.name = input.name + '-' + addedContactNum;
  });

  const newLabels = newRow.querySelectorAll('label');
  newLabels.forEach(function (label) {
    label.htmlFor = label.htmlFor + '-' + addedContactNum;
  });
  addedContactNum++;

  inputContainer.insertBefore(newRow, template);
  const deleteBtns = Array.from(document.querySelectorAll('.delete-contact'));

  deleteBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      deleteContactField(e.target);
    });
  });
}

function deleteContactField(el) {
  const nodeName = el.nodeName;
  const inputContainer =
    nodeName == 'use'
      ? el.parentElement.parentElement.parentElement
      : nodeName == 'svg'
      ? el.parentElement.parentElement
      : el.parentElement;

  inputContainer.remove();
}

function attachEventHandlers() {
  FORM.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!allResponsesValid()) return;
    submitForm();
  });

  const fieldsNeedingValidation = Array.from(
    document.querySelectorAll('#grant-access input')
  );
  fieldsNeedingValidation.forEach((q) => {
    q.addEventListener('blur', (e) => {
      performValidations(e.target);
    });
  });

  const addContactButtons = Array.from(
    document.querySelectorAll('.add-contact')
  );
  addContactButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      appendContactField(e.target);
    });
  });
}

function init() {
  attachEventHandlers();
}

init();
