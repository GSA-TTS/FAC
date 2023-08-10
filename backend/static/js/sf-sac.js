import { checkValidity } from './validate';

const FORM = document.forms[0];

function setFormDisabled(shouldDisable) {
  const continueBtn = document.getElementById('continue');
  continueBtn.disabled = shouldDisable;
}

function allResponsesValid() {
  const inputsWithErrors = document.querySelectorAll('[class *="--error"]');
  return inputsWithErrors.length === 0;
}

function performValidations(field) {
  const inputType = field.type;
  if (inputType == 'radio') {
    const rgInputs = document.querySelectorAll(
      'input[name="' + field.name + '"]'
    );
    rgInputs.forEach((i) => i.classList.remove('usa-input--error'));
  }
  const errors = checkValidity(field);
  setFormDisabled(errors.length > 0);
}

function highlightActiveNavSection() {
  let currentFieldsetId;
  const fieldsets = document.querySelectorAll('fieldset[id]');
  const navLinks = document.querySelectorAll('li .usa-sidenav__item a');

  fieldsets.forEach((f) => {
    const fieldsetTop = f.offsetTop;
    if (scrollY >= fieldsetTop + 100) {
      currentFieldsetId = f.id;
    }
  });

  navLinks.forEach((l) => {
    if (currentFieldsetId) {
      l.classList.remove('usa-current');
    }

    if (l.getAttribute('href') == `#${currentFieldsetId}`) {
      l.classList.add('usa-current');
    }
  });
}

function attachEventHandlers() {
  const fieldsNeedingValidation = Array.from(
    document.querySelectorAll('.sf-sac input[data-validate-not-null]')
  );

  FORM.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!allResponsesValid()) return;
    FORM.submit();
  });

  fieldsNeedingValidation.forEach((q) => {
    q.addEventListener('blur', (e) => {
      performValidations(e.target);
    });
  });

  const rbInputs = document.querySelectorAll('[name="audit_period_covered"]');
  const monthsInput = document.querySelector('#audit_period_other_months');
  rbInputs.forEach((input) => {
    input.addEventListener('change', () => {
      if (input.id == 'audit-period-other') {
        monthsInput.removeAttribute('disabled');
      } else {
        monthsInput.setAttribute('disabled', true);
      }
    });
  });

  window.addEventListener('scroll', highlightActiveNavSection);
}

function init() {
  attachEventHandlers();
}

init();
