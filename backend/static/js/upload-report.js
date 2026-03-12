var FORM = document.getElementById('upload-report__form');

const continueButton = document.getElementById(`continue`); // <button>
const loader = document.getElementById(`loader`); // <div>
const keepPreviousCheckbox = document.getElementById('keep-previous-report'); // <input> (may be null)

// On form submission, display the loader and disable the submit button
function attachUploadHandler() {
  FORM.addEventListener('submit', () => {
    loader.hidden = false;
    continueButton.innerText = 'Validating...';
    continueButton.disabled = true;
  });
}

// On resubmission, if a user chooses to keep their previously uploaded report, grey out the other inputs.
// To allow the user to actually submit the form, we remove the "required" attribute from the other inputs.
function attachKeepPreviousHandler() {
  if (!keepPreviousCheckbox) return;

  keepPreviousCheckbox.addEventListener('change', () => {
    const isChecked = keepPreviousCheckbox.checked;

    const pageInputs = FORM.querySelectorAll('input[type="number"]');
    pageInputs.forEach((input) => {
      input.disabled = isChecked;
      if (isChecked) input.removeAttribute('required');
    });

    const fileInput = FORM.querySelector('input[type="file"]');
    if (fileInput) {
      fileInput.disabled = isChecked;
      if (isChecked) {
        fileInput.removeAttribute('required');
      } else {
        fileInput.setAttribute('required', '');
      }
    }
  });
}

// On pageload, attach handlers to monitor the page state
function attachEventHandlers() {
  attachUploadHandler();
  attachKeepPreviousHandler();
}

function init() {
  attachEventHandlers();
}

init();
