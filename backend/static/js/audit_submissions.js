function init() {
  const START_SUBMISSION_URL = '../report_submission/eligibility/';
  addEventHandlers(START_SUBMISSION_URL);
}

function addEventHandlers(START_SUBMISSION_URL) {
  // Start new submission form
  const terms_form = document.querySelector('#start-new-submission');
  const terms_checkbox = terms_form.querySelector(
    '#check-start-new-submission'
  );
  const terms_start_sub = terms_form.querySelector('#start-submission');
  terms_form.addEventListener('submit', (e) => {
    e.preventDefault();
  });
  terms_checkbox.addEventListener('change', (e) => {
    e.target.checked == true
      ? (terms_start_sub.disabled = false)
      : (terms_start_sub.disabled = true);
  });
  terms_start_sub.addEventListener('click', () => {
    window.location.href = START_SUBMISSION_URL;
  });
}

init();
