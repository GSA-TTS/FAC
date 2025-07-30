function init() {
  addEventHandlers();
}

function addEventHandlers() {
  // Start new submission form.
  // Enables the submit button when the terms checkbox is clicked.
  const terms_form = document.querySelector('#start-new-submission');
  const terms_checkbox = terms_form.querySelector(
    '#check_start_new_submission'
  );
  const terms_start_sub = terms_form.querySelector('#start-submission');
  terms_checkbox.addEventListener('change', (e) => {
    e.target.checked == true
      ? (terms_start_sub.disabled = false)
      : (terms_start_sub.disabled = true);
  });
}

init();
