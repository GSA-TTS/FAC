// Grab useful page elements, such as aliased variables and input fields
const sac_id = JSON.parse(document.getElementById('sac_id').textContent);
const view_id = JSON.parse(document.getElementById('view_id').textContent);
const fileupload = document.getElementById(`file-input-${view_id}-xlsx`);

// Set disabled status of the "Save and continue" button
function setSubmitButtonDisabled(disabled) {
  const submitButton = document.getElementById('continue');
  submitButton.disabled = disabled;
}

// On pageload, attach handlers to monitor the page state
function attachEventHandlers() {
  setSubmitButtonDisabled(true);

  // On file upload, send it off for validation
  fileupload.addEventListener('change', (e) => {
    var data = new FormData();
    data.append('FILES', e.target.files[0]);
    data.append('filename', e.target.files[0].name);
    data.append('sac_id', sac_id);

    fetch(`/audit/excel/${sac_id}`, {
      method: 'POST',
      body: data,
    }).then((response) => {
      if (response.status == 200) {
        console.log('Excel file successfully validated.');
        setSubmitButtonDisabled(false);
      } else {
        console.error('Error when validating excel file.\n', response);
      }
    });
  });
}

function init() {
  attachEventHandlers();
}

init();
