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
      if (isChecked) {
        input.removeAttribute('required')
      } else if (input.name != "CAP_page" && input.name != "schedule_prior_findings") {
        input.setAttribute('required', 'true'); 
      };
    });

    // USWDS styled file inputs are acted upon with JS on mount. This messes with the default disabled/enabled states.
    // From the USWDS file input class, "dropZone" is the parent element on which classes should be added/revoked. In this case, it's a div.
    // To change the disabled/enabled styling, we add or remove the appropriate top level class.
    // Source: https://github.com/uswds/uswds/blob/develop/packages/usa-file-input/src/index.js
    const fileInput = FORM.querySelector('input[type="file"]');
    if (fileInput) {
      const dropZone = fileInput.closest('.usa-file-input');
      if (isChecked) {
        fileInput.disabled = true;
        fileInput.removeAttribute('required');
        if (dropZone) dropZone.classList.add('usa-file-input--disabled');
      } else {
        fileInput.disabled = false;
        fileInput.setAttribute('required', 'true');
        if (dropZone) {
          dropZone.classList.remove('usa-file-input--disabled');
          dropZone.removeAttribute('aria-disabled');
        }
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
