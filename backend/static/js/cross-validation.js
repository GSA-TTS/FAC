var FORM = document.getElementById('cross-validation');

const validation_button = document.getElementById(`begin-validation`); // <button>
const loader = document.getElementById(`loader`); // <div>

// On form submission, display the loader and disable the submit button
function attachValidationHandler() {
  FORM.addEventListener('submit', () => {
    loader.hidden = false;
    validation_button.innerText = 'Validating...';
    validation_button.disabled = true;
  });
}

// On pageload, attach handlers to monitor the page state
function attachEventHandlers() {
  attachValidationHandler();
}

function init() {
  attachEventHandlers();
}

init();
