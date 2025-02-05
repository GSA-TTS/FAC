import { checkValidity } from './validate';

let addedContactNum = 1;

function setFormDisabled(shouldDisable) {
  const continueBtn = document.getElementById('create');
  continueBtn.disabled = shouldDisable;
}

function performValidations(nodes) {
  const errors = Array.from(nodes).filter((field) => {
    return checkValidity(field).length > 0;
  });
  setFormDisabled(errors.length > 0);
}

function insertInc(elements, attr, splitter, inc) {
  elements.forEach(function (el) {
    let newVal = el[attr].replace(splitter, '');
    newVal = newVal + '_' + inc + splitter;
    el.setAttribute(attr, newVal);
  });
}
function appendInc(elements, attr, inc) {
  elements.forEach(function (el) {
    const newVal = el.getAttribute(attr) + '_' + inc;
    el.setAttribute(attr, newVal);
  });
}
function appendContactField(btnEl) {
  const inputContainer = btnEl.parentElement;
  const template = inputContainer.querySelector('template');
  const newRow = template.content.cloneNode(true);

  const newInputs = newRow.querySelectorAll('input');
  newInputs.forEach((q, key, arr) => {
    attachFocusoutMulti(newInputs);
    if (key === arr.length - 1) {
      const newMatchVal = newInputs[key - 1].id + '_' + addedContactNum;
      q.setAttribute('data-validate-must-match', newMatchVal);
    }
    if (key in [0, 1]) {
      const newMatchVal = newInputs[(key ^= 1)].id + '_' + addedContactNum;
      q.setAttribute('data-validate-matched-field', newMatchVal);
    }
  });
  const newLabels = newRow.querySelectorAll('label');
  const nrErrorMsgs = newRow.querySelectorAll('.usa-error-message');
  const nrErrorItems1 = newRow.querySelectorAll('li[id$="-not-null"]');
  const nrErrorItems2 = newRow.querySelectorAll('li[id$="-email"]');
  const nrErrorItems3 = newRow.querySelectorAll('li[id$="-must-match"]');
  const nrErrorItems4 = newRow.querySelectorAll('li[id$="-matched-field"]');

  appendInc(newInputs, 'id', addedContactNum);
  appendInc(newLabels, 'for', addedContactNum);
  insertInc(nrErrorMsgs, 'id', '-error-message', addedContactNum);
  insertInc(nrErrorItems1, 'id', '-not-null', addedContactNum);
  insertInc(nrErrorItems2, 'id', '-email', addedContactNum);
  insertInc(nrErrorItems3, 'id', '-must-match', addedContactNum);
  insertInc(nrErrorItems4, 'id', '-matched-field', addedContactNum);

  addedContactNum++;

  inputContainer.insertBefore(newRow, template);
  const deleteBtns = Array.from(document.querySelectorAll('.delete-contact'));

  deleteBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      deleteContactField(btn);
    });
  });
}

function deleteContactField(el) {
  el.parentElement.parentElement.parentElement.remove();
}

function attachFocusoutMulti(elements) {
  elements.forEach((p) => {
    p.addEventListener('focusout', () => {
      performValidations(elements);
    });
  });
}

function attachEventHandlers() {

  const continueBtn = document.getElementById('create');
  continueBtn.addEventListener('click', (e) => {
    e.preventDefault();
    setFormDisabled(true);
    document.getElementById('grant-access').submit();
  });

  const certifyingInputs = Array.from(
    document.querySelectorAll(
      '#grant-access input:not(.auditee_contacts input, .auditor_contacts input)'
    )
  );

  certifyingInputs.forEach((q) => {
    q.addEventListener('focusout', (e) => {
      performValidations([e.target]);
    });
  });

  const addContactButtons = Array.from(
    document.querySelectorAll('.add-contact')
  );
  addContactButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      appendContactField(btn);
    });
  });
  const contactsCollections = Array.from(
    document.querySelectorAll('.auditee_contacts, .auditor_contacts')
  );
  contactsCollections.forEach((q) => {
    const accFields = Array.from(q.querySelectorAll('input'));
    attachFocusoutMulti(accFields);
  });
}

function init() {
  attachEventHandlers();
}

init();
