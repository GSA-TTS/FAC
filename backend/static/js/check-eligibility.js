import { getCookie } from "./csrft";

const csrftoken = getCookie('csrftoken');
const SUBMISSION_URL = '/report_submission/eligibility/';
const NEXT_URL = '../auditeeinfo';
const FORM = document.forms[0];

function submitForm() {
  const formData = serializeFormData(new FormData(FORM));
  formData.met_spending_threshold = stringToBoolean(
      formData.met_spending_threshold
  );
  formData.is_usa_based = stringToBoolean(formData.is_usa_based);
  fetch(SUBMISSION_URL, {
    method: "POST",
    headers: {'X-CSRFToken': csrftoken},
    body: JSON.stringify(formData)
  }).then((resp) => resp.json()).then((data) => handleEligibilityResponse(data)).catch((e) => handleErrorResponse(e));
}

function handleEligibilityResponse(data) {
    console.log(data.errors);
    window.location.href = NEXT_URL;
}

function handleErrorResponse(e) {
  console.log('ERROR: Form submission error. ' + e);
  window.location.href = NEXT_URL;
}

function serializeFormData(formData) {
  return Object.fromEntries(formData);
}

function isValidEntity({name, id}) {
  const INVALID_ENTITY_TYPES = {
    user_provided_organization_type: ["entity-none"],
    met_spending_threshold: ["spend-no"],
    is_usa_based: ["us-no"],
  };

  return !INVALID_ENTITY_TYPES[name].includes(id);
}

function stringToBoolean(value) {
  if (value && typeof value === "string") {
    if (value.toLowerCase() === "true") return true;
    if (value.toLowerCase() === "false") return false;
  }
  return value;
}

function setFormDisabled(shouldDisable) {
  const continueBtn = document.getElementById("continue");
  continueBtn.disabled = shouldDisable;
}

function resetErrorStates(el) {
  const inputsWithErrors = Array.from(el.querySelectorAll(".usa-radio--error"));
  inputsWithErrors.forEach((i) => i.classList.remove("usa-radio--error"));
}

function validateEntity(entity) {
  const radioEl = entity.parentElement;
  const fieldsetEl = radioEl.parentElement;
  resetErrorStates(fieldsetEl);

  if (!isValidEntity(entity) && entity.checked) {
    radioEl.classList.add("usa-radio--error");
  }
}

function runAllValidations() {
  const inputs = Array.from(document.querySelectorAll(".question input"));
  const validations = [validateEntity];

  inputs.forEach((input) => {
    validations.forEach((validation) => validation(input));
  });

  const allValid = allResponsesValid();
  setFormDisabled(!allValid);
}

function allResponsesValid() {
  const inputsWithErrors = document.querySelectorAll('[class *="--error"]');
  return inputsWithErrors.length === 0;
}

function attachEventHandlers() {
  FORM.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!allResponsesValid()) return;
    submitForm();
  });

  const questions = Array.from(document.querySelectorAll(".question"));
  questions.forEach((q) => {
    q.addEventListener("change", (e) => {
      validateEntity(e.target);
      runAllValidations();
    });
  });
}

function init() {
  attachEventHandlers();
  runAllValidations(); // Run these on load in case the user refreshed
}

init();
