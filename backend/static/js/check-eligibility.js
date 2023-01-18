<<<<<<< Updated upstream
const URL = '/report_submission/eligibility/';
const FORM = document.forms[0];

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');
=======
import { queryAPI } from "./api";

const SUPPRESS_ERROR_FOR_TEST = true; // REMOVE after submission error fixed.

const URL = "/report_submission/eligibility";
const NEXT_URL = "../auditeeinfo/";
const FORM = document.forms[0];
>>>>>>> Stashed changes

function submitForm() {
  const formData = serializeFormData(new FormData(FORM));
  formData.met_spending_threshold = stringToBoolean(
<<<<<<< Updated upstream
      formData.met_spending_threshold
  );
  formData.is_usa_based = stringToBoolean(formData.is_usa_based);
  fetch(URL, {
    method: "POST",
    headers: {'X-CSRFToken': csrftoken},
    body: JSON.stringify(formData)
  }).then((resp) => resp.json()).then((data) => handleEligibilityResponse(data)).catch((e) => handleErrorResponse(e));
}

function handleEligibilityResponse(data) {
  if (data.eligible) {
    const nextUrl = '../auditeeinfo/';
    window.location.href = nextUrl;
  } else {
    console.log(data.errors);
  }
}

function handleErrorResponse(e) {
  console.error(e);
  console.log('ERROR: Form submission error.');
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

=======
    formData.met_spending_threshold
  );
  formData.is_usa_based = stringToBoolean(formData.is_usa_based);

  queryAPI(
    URL,
    formData,
    {
      method: "POST",
    },
    [handleEligibilityResponse, handleErrorResponse]
  );
}
function handleEligibilityResponse(data) {
  console.log("SUCCESS: Form submitted. " + data);
  if (data.eligible) {
    window.location.href = NEXT_URL;
  } else {
    console.log(data.errors);
  }
}
function handleErrorResponse(e) {
  console.log("ERROR: Form submission error. " + e);
  // REMOVE below after reposnse error is fixed.
  if (SUPPRESS_ERROR_FOR_TEST) {
    window.location.href = NEXT_URL;
  }
  // END REMOVE
}

function serializeFormData(formData) {
  return Object.fromEntries(formData);
}

function isValidEntity({ name, id }) {
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

>>>>>>> Stashed changes
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
