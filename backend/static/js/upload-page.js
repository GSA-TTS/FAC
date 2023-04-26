// Matches current URL against the correct upload endpoint
// URLs defined in /audit/urls.py come from /audit/fixtures/excel.py
const upload_urls = {
  'federal-awards': 'FederalAwardsExpended',
  'audit-findings': 'FindingsUniformGuidance',
  'audit-findings-text': 'FindingsText',
  CAP: 'CorrectiveActionPlan',
};

// Useful page elements, such as aliased variables and input fields
const sac_id = JSON.parse(document.getElementById('sac_id').textContent);
const view_id = JSON.parse(document.getElementById('view_id').textContent);
const file_input = document.getElementById(`file-input-${view_id}-xlsx`);
const info_box = document.getElementById(`info_box`);

// Set disabled status of the "Save and continue" button
function setSubmitButtonDisabled(disabled) {
  const submitButton = document.getElementById('continue');
  submitButton.disabled = disabled;
}

// On pageload, attach handlers to monitor the page state
function attachEventHandlers() {
  setSubmitButtonDisabled(true);

  // On file upload, send it off for validation
  file_input.addEventListener('change', (e) => {
    try {
      // Ex. 'FederalAwardsExpended' from URL including 'federal-awards'
      const currentURL = new URL(window.location.href);
      const report_submission_url =
        upload_urls[currentURL.pathname.split('/')[2]];

      if (!e.target.files[0]) {throw "No file chosen"}
      var data = new FormData();
      data.append('FILES', e.target.files[0]);
      data.append('filename', e.target.files[0].name);
      data.append('sac_id', sac_id);

      info_box.hidden = false;
      info_box.innerHTML = 'Validating your file...';

      fetch(`/audit/excel/${report_submission_url}/${sac_id}`, {
        method: 'POST',
        body: data,
      }).then((response) => {
        if (response.status == 200) {
          info_box.innerHTML = 'File successfully validated!';
          setSubmitButtonDisabled(false);
        } else {
          info_box.innerHTML = 'Error on validation. See console for more information.';
          console.error('Error when validating excel file.\n', response);
        }
      });
    } catch (error) {
      console.error('Error when sending excel file.\n', error);
    }
  });
}

function init() {
  attachEventHandlers();
}

init();
