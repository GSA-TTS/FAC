import { checkValidity } from './validate';

const FORM = document.forms[0];
let addedContactNum = 1;

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
    FORM.submit();
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
