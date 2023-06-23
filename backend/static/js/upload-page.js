/*
  Candidate(s) for global constants
*/
// Matches current URL against the correct upload endpoint. Comes from /audit/fixtures/excel.py
const UPLOAD_URLS = {
  'federal-awards': 'federal-awards-expended',
  'audit-findings': 'findings-uniform-guidance',
  'audit-findings-text': 'findings-text',
  'additional-ueis': 'additional-ueis',
  CAP: 'corrective-action-plan',
};

/*
  Useful page elements
*/
const sac_id = JSON.parse(document.getElementById('sac_id').textContent);
const view_id = JSON.parse(document.getElementById('view_id').textContent);
const file_input = document.getElementById(`file-input-${view_id}-xlsx`);
const info_box = document.getElementById(`info_box`);
const already_submitted = document.getElementById(`already-submitted`);

/* 
  Function definitions
*/
// Disable/enable "Continue" button
function setContinueButtonDisabled(disabled) {
  const submitButton = document.getElementById('continue');
  submitButton.disabled = disabled;
}

// Print helpful error info to page & console on unsuccessful upload
function handleUploadErrors(error) {
  if (typeof error.text === 'function') {
    error.text().then((errorMessage) => {
      console.error(
        'Error when sending excel file.\n',
        JSON.parse(errorMessage)
      );
      info_box.innerHTML =
        'Error when uploading file. See the console for more information.';
    });
  } else if (error.name === 'AbortError') {
    console.error(`Timeout - Response took longer than expected.\n`, error);
    info_box.innerHTML = `Timeout - Response took longer than expected.`;
  } else console.error(`Unexpected error.\n`, error);
}

// On file upload, send it off for verification.
// TODO: Enable timeout on too-long verifications
/*
const UPLOAD_TIMEOUT = 15000; // 15s - Global?
const abortController = new AbortController();
const signal = abortController.signal;
setTimeout(() => {
  abortController.abort();
}, UPLOAD_TIMEOUT);
// include signal in fetch body
*/
function attachFileUploadHandler() {
  file_input.addEventListener('change', (e) => {
    try {
      info_box.hidden = false;
      info_box.innerHTML = 'Validating your file...';

      const currentURL = new URL(window.location.href);
      const report_submission_url =
        UPLOAD_URLS[currentURL.pathname.split('/')[2]];
      if (!report_submission_url) throw 'No upload URL available.';
      if (!e.target.files[0]) throw 'No file selected.';
      if (e.target.files[0].name.split('.').pop() !== 'xlsx')
        throw 'File type not accepted.';

      var data = new FormData();
      data.append('FILES', e.target.files[0]);
      data.append('filename', e.target.files[0].name);
      data.append('sac_id', sac_id);

      fetch(`/audit/excel/${report_submission_url}/${sac_id}`, {
        method: 'POST',
        body: data,
      })
        .then((response) => {
          if (response.status == 200) {
            info_box.innerHTML =
              'File successfully validated! Your work has been saved.';
            setContinueButtonDisabled(false);
          } else {
            // TODO: Handle helpful validation errors here
            console.error('Error when validating excel file.\n', response);
            info_box.innerHTML =
              'Error on validation. See the console for more information.';
          }
        })
        .catch((error) => {
          handleUploadErrors(error);
        });
    } catch (error) {
      info_box.innerHTML = `Error when sending excel file.\n ${error}`;
      console.error('Error when sending excel file.\n', error);
    }
  });
}

// On pageload, attach handlers to monitor the page state
function attachEventHandlers() {
  attachFileUploadHandler();
}

function init() {
  attachEventHandlers();

  already_submitted
    ? setContinueButtonDisabled(false)
    : setContinueButtonDisabled(true);
}

init();
