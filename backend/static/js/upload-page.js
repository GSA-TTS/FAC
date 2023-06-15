/*
  Candidate(s) for global constants
*/
// Matches current URL against the correct upload endpoint. Comes from /audit/fixtures/excel.py
const UPLOAD_URLS = {
  'federal-awards': 'FederalAwardsExpended',
  'audit-findings': 'FindingsUniformGuidance',
  'audit-findings-text': 'FindingsText',
  CAP: 'CorrectiveActionPlan',
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
        'Error when uploading file. See the console for more information, or contact an administrator.';
    });
  } else if (error.name === 'AbortError') {
    console.error(`Timeout - Response took longer than expected.\n`, error);
    info_box.innerHTML = `Timeout - Response took longer than expected. Try again later.`;
  } else {
    info_box.innerHTML =
      'Error when uploading file. Ensure you have upload the correct template, or contact an administrator.';
    console.error(`Unexpected error.\n`, error);
  }
}

function getValidationErrorsTable(res) {
  var rows_html = '';
  var row_array = [];
  for (let i = 0; i < res.errors.length; i++) {
    row_array = res.errors[i].replaceAll(/[()']/g, ` `).split(',');
    rows_html += `
    <tr>
      <td class="text-center">${row_array[0]}</p>
      <td class="text-center">${row_array[1]}</p>
      <td>${row_array[2]}</p>
    </tr>`;
  }
  const validationTable = `<p>Error on validation. Check the following cells for errors, and re-upload. 
  Common errors include incorrect data types or missing information.</p>
  <table class="usa-table usa-table--striped">
    <thead>
      <tr>
        <th scope="col">Row</th>
        <th scope="col">Column</th>
        <th scope="col">Field</th>
      </tr>
    </thead>
    <tbody>
      ${rows_html}
    </tbody>
  </table>`;
  return validationTable;
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
        .then((res) => res.json())
        .then((res) => {
          if (res.status == 200) {
            info_box.innerHTML =
              'File successfully validated! Your work has been saved.';
            setContinueButtonDisabled(false);
          } else {
            info_box.innerHTML = getValidationErrorsTable(res);
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
