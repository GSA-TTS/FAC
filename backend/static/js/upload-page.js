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
  'secondary-auditors': 'secondary-auditors',
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
function setFormDisabled(shouldDisable) {
  const submitButton = document.getElementById('continue');
  submitButton.disabled = shouldDisable;
}

// Print helpful error info to page & console on unsuccessful upload
function handleErrorOnUpload(error) {
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
      'Error when uploading file. Ensure you have uploaded the correct template, or contact an administrator.';
    console.error(`Unexpected error.\n`, error);
  }
}

function get_error_table(data) {
  var rows_html = '';
  var row_array = [];
  for (let i = 0; i < data.errors.length; i++) {
    // Convert given string-tuples into arrays:
    // "(col, row...)" -> [col, row, ...]
    row_array = data.errors[i];
    row_array = JSON.parse(
      row_array.replaceAll('(', '[').replaceAll(')', ']').replaceAll(`'`, `"`)
    );

    rows_html += `
    <tr>
      <td class="text-center">${row_array[0]}${row_array[1]}</td>
      <td>${row_array[2]}</td>
      <td>${row_array[3]['text']}.</td>
    </tr>`;
    // <a class="usa-link" href="${row_array[3]["link"]}">Link</a>
  }
  const validationTable = `<p>Error on validation. Check the following cells for errors, and re-upload. 
  Common errors include incorrect data types or missing information.</p>
  <table class="usa-table usa-table--striped">
    <thead>
      <tr>
        <th scope="col">Cell</th>
        <th scope="col">Field</th>
        <th scope="col">Help Text</th>
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

      const current_url = new URL(window.location.href);
      const report_submission_url =
        UPLOAD_URLS[current_url.pathname.split('/')[2]];
      if (!report_submission_url) throw 'No upload URL available.';
      if (!e.target.files[0]) throw 'No file selected.';
      if (e.target.files[0].name.split('.').pop() !== 'xlsx')
        throw 'File type not accepted.';

      var body = new FormData();
      body.append('FILES', e.target.files[0]);
      body.append('filename', e.target.files[0].name);
      body.append('sac_id', sac_id);

      fetch(`/audit/excel/${report_submission_url}/${sac_id}`, {
        method: 'POST',
        body: body,
      })
        .then((res) => {
          if (res.status == 200) {
            info_box.innerHTML =
              'File successfully validated! Your work has been saved.';
            setFormDisabled(false);
          } else {
            res.json().then((data) => {
              if (data.type === 'error_row') {
                if (Array.isArray(data.errors[0]))
                  handleErrorOnUpload(new Error(data.errors[0]));
                info_box.innerHTML = get_error_table(data);
              } else if (data.type === 'error_field') {
                info_box.innerHTML = `Field Error: ${data.errors}`;
              } else if (data.type === 'no_late_changes') {
                info_box.innerHTML =
                  'Access denied. Further changes to audits that have been marked ready for certification are not permitted.';
              } else if (res.status == 400) {
                info_box.innerHTML = 'Field Error: undefined';
                setFormDisabled(false);
              } else if (data.type) {
                info_box.innerHTML = `Error: ${data.errors}`;
              } else {
                throw new Error('Returned error type is missing!');
              }
            });
          }
        })
        .catch((error) => {
          handleErrorOnUpload(error);
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

  already_submitted ? setFormDisabled(false) : setFormDisabled(true);
}

init();
