var FORM = document.getElementById('upload-report__form');

const continueButton = document.getElementById(`continue`); // <button>
const loader = document.getElementById(`loader`); // <div>

// On form submission, display the loader and disable the submit button
function attachUploadHandler() {
  FORM.addEventListener('submit', () => {
    loader.hidden = false;
    continueButton.innerText = 'Validating...';
    continueButton.disabled = true;
  });
}

// On pageload, attach handlers to monitor the page state
function attachEventHandlers() {
  attachUploadHandler();
}

function init() {
  attachEventHandlers();
}

init();
