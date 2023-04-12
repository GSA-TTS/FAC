const fileupload = document.getElementById('file-input-audit-findings-xlsx');

function setFormEnabled(shouldEnable) {
  const continueBtn = document.getElementById('continue');
  continueBtn.disabled = !shouldEnable;
}

function attachEventHandlers() {
  setFormEnabled(false);

  fileupload.addEventListener('change', (e) => {
    const sac_id = JSON.parse(document.getElementById('sac_id').textContent);

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
        setFormEnabled(true);
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
