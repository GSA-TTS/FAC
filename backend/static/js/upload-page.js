import { UPLOAD_TIMEOUT, UPLOAD_URLS } from './globals';

/*
  Useful page elements
*/
const sac_id = JSON.parse(document.getElementById('sac_id').textContent); // String
const view_id = JSON.parse(document.getElementById('view_id').textContent); // String
const already_submitted = document.getElementById(`already-submitted`); // Boolean

const file_input = document.getElementById(`file-input-${view_id}-xlsx`); // <input type="file">
const info_box = document.getElementById(`info_box`); // <div>

/* 
  Function definitions
*/
// Disable/enable "Continue" button
function setFormDisabled(shouldDisable) {
  const submitButton = document.getElementById('continue');
  submitButton.disabled = shouldDisable;
}

// Print helpful error info to page & console on unsuccessful upload
function handleErrors(error) {
  if (typeof error.text === 'function') {
    // The request never made it to the server. Suggests a local issue.
    error.text().then((message) => {
      console.error('Error when uploading file.', JSON.parse(message));
      info_box.innerHTML =
        'There was an error when uploading the file. If this issue persists, contact an administrator.';
    });
  } else if (error.name === 'AbortError') {
    // Timeout from the frontend.
    console.error(`Timeout - Response took longer than expected.\n`, error);
    info_box.innerHTML = `Timeout - Response took longer than expected. Please try again later. If this issue persists, contact an administrator.`;
  } else if (error.name === 'Field error') {
    // Incorrect file template (probably).
    console.error(`Field error.\n`, error);
    info_box.innerHTML = `A field is missing in the uploaded file. Ensure you have uploaded the correct workbook, or contact an administrator. ${error}`;
  } else if (error.name === 'Row error') {
    // Unhelpful row error (not table-able). Suggests an issue in validation error reporting.
    console.error(`Row error (unable to convert to table).\n`, error);
    info_box.innerHTML = `There was an unexpected error when validating the file. Please ensure you have uploaded the correct workbook. If this issue persists, contact an administrator.`;
  } else if (error.name === 'Access denied') {
    // User is attempting to change their file after certifying.
    console.error(`Access denied. Audit is locked to SF-SAC changes.\n`, error);
    info_box.innerHTML =
      'Access denied. Further changes to audits that have been marked ready for certification are not permitted.';
  } else if (error.name === 'Unknown workbook') {
    // Unknown workbook.
    console.error(
      `Unknown workbook - The uploaded workbook template does not originate from SF-SAC.\n`,
      error
    );
    info_box.innerHTML = `This does not look like a GSA SF-SAC workbook. Please download a workbook template from fac.gov for entering and submitting SF-SAC data.`;
  } else {
    // Catch all.
    console.error(`Unexpected error.\n`, error);
    info_box.innerHTML = `There was an unexpected error when validating the file. Please try again later. If this issue persists, contact an administrator. Error: ${error}`;
  }
}

function display_error_table(data) {
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
    // TODO: Add this link once the site is hosting elpful information.
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

  info_box.innerHTML = validationTable;
}

// On file upload, send it off for verification.
function attachFileUploadHandler() {
  file_input.addEventListener('change', (e) => {
    try {
      info_box.hidden = false;
      if (already_submitted) already_submitted.hidden = true;
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

      const abortController = new AbortController();
      const signal = abortController.signal;
      setTimeout(() => {
        abortController.abort();
      }, UPLOAD_TIMEOUT);

      fetch(`/audit/excel/${report_submission_url}/${sac_id}`, {
        method: 'POST',
        body: body,
        signal: signal,
      })
        .then((res) => {
          // If recieving a 200 response, we are done.
          // Otherwise, pull the JSON data from the reponse and react accordingly.
          if (res.status == 200) {
            info_box.innerHTML =
              'File successfully validated! Your work has been saved.';
            setFormDisabled(false);
          } else {
            res.json().then((data) => {
              if (data.type === 'error_row') {
                // Issue in the rows. The "good" error, which we can use to display the error table.
                // There can also be 'error_row' data that is just an unhelpful array.
                if (Array.isArray(data.errors[0])) {
                  let e = new Error(`Row error: ${data.errors[0]}`);
                  e.name = 'Row error';
                  handleErrors(new Error(data.errors[0]));
                } else {
                  display_error_table(data);
                }
              } else if (data.type === 'error_field') {
                let e = new Error(data.errors);
                e.name = 'Field error';
                handleErrors(e);
              } else if (data.type === 'no_late_changes') {
                let e = new Error(data.errors);
                e.name = 'Access denied';
                handleErrors(e);
              } else if (data.type === 'unknown_workbook') {
                let e = new Error(data.errors);
                e.name = 'Unknown workbook';
                handleErrors(e);
              } else {
                // Catch all.
                let e = new Error('Unexpected error in JSON response.');
                e.name = 'Unexpected';
                handleErrors(e);
              }
            });
          }
        })
        .catch((error) => {
          handleErrors(error);
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
