const FORM = document.forms[0];
const fileupload = document.getElementById('file-input-federal-awards-xlsx');

function setFormEnabled(shouldEnable) {
    const continueBtn = document.getElementById('continue');
    continueBtn.disabled = !shouldEnable;
}

function attachEventHandlers() {
    setFormEnabled(false)

    fileupload.addEventListener('change', (e) => {
        console.log(e)
        // FORM.submit();
        setFormEnabled(true)
    });
}

function init() {
    attachEventHandlers();
}
  
init();